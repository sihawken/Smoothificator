# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Copyright (c) [2025] [Roman Tenger]
import re
import sys
import logging
import os
import argparse
import math

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Configure logging
log_file_path = os.path.join(script_dir, "smooth_wall_log.txt")
logging.basicConfig(
    filename=log_file_path,
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def get_layer_height(gcode_lines):
    """Extract layer height from G-code header comments"""
    for line in gcode_lines:
        if "layer_height =" in line.lower():
            match = re.search(r'; layer_height = (\d*\.?\d+)', line, re.IGNORECASE)
            if match:
                return float(match.group(1))
    return None

def get_min_layer_height(gcode_lines):
    """Extract minimum layer height from G-code header comments"""
    for line in gcode_lines:
        if "min_layer_height =" in line.lower():
            match = re.search(r'; min_layer_height = (\d*\.?\d+)', line, re.IGNORECASE)
            if match:
                return float(match.group(1))
    return None

def process_gcode(input_file, outer_layer_height=None):
    current_layer = 0
    current_z = 0.0
    current_layer_height = 0.0
    in_external_perimeter = False
    external_block_lines = []
    
    logging.info("Starting G-code processing")
    logging.info(f"Input file: {input_file}")
    logging.info(f"Desired outer wall height: {outer_layer_height}mm")

    # Read the input G-code
    with open(input_file, 'r') as infile:
        lines = infile.readlines()

    # Get outer layer height from G-code if not provided
    if outer_layer_height is None:
        outer_layer_height = get_min_layer_height(lines)
        if outer_layer_height is None:
            logging.error("Could not find min_layer_height in G-code and no value provided")
            sys.exit(1)

    logging.info(f"Using outer wall height: {outer_layer_height}mm")

    # Validate outer layer height
    if outer_layer_height <= 0:
        logging.error(f"Outer layer height ({outer_layer_height}mm) must be greater than 0")
        sys.exit(1)
    
    # Process the G-code
    modified_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Detect layer changes and get layer height
        if ";LAYER_CHANGE" in line:
            current_layer += 1
            # Look ahead for HEIGHT marker
            for j in range(i + 1, min(i + 5, len(lines))):
                if ";HEIGHT:" in lines[j]:
                    height_match = re.search(r';HEIGHT:([\d.]+)', lines[j])
                    if height_match:
                        current_layer_height = float(height_match.group(1))
                        logging.info(f"Layer {current_layer} detected with height={current_layer_height:.3f}")
                        break
            modified_lines.append(line)
            i += 1
            continue

        # Get current Z position
        if line.startswith("G1 Z"):
            z_match = re.search(r'Z([-\d.]+)', line)
            if z_match:
                current_z = float(z_match.group(1))
            modified_lines.append(line)
            i += 1
            continue

        # Start of external perimeter block
        if ";TYPE:External perimeter" in line or ";TYPE:Outer wall" in line:
            external_block_lines = []
            # Collect all lines until next type change or empty line
            while i < len(lines):
                current_line = lines[i]
                if i + 1 < len(lines) and (";TYPE:" in lines[i + 1] or "M" in lines[i + 1] and not "M73" in lines[i + 1]):
                    external_block_lines.append(current_line)
                    i += 1
                    break
                external_block_lines.append(current_line)
                i += 1

            # Process the collected block
            if external_block_lines:
                if current_layer_height > outer_layer_height:
                    # Calculate both ceiling and floor passes
                    passes_ceil = math.ceil(current_layer_height / outer_layer_height)
                    passes_floor = math.floor(current_layer_height / outer_layer_height)
                    
                    # Calculate resulting height per pass for both options
                    height_per_pass_ceil = current_layer_height / passes_ceil
                    height_per_pass_floor = current_layer_height / passes_floor if passes_floor > 0 else float('inf')
                    
                    # Calculate differences from desired height
                    diff_ceil = abs(height_per_pass_ceil - outer_layer_height)
                    diff_floor = abs(height_per_pass_floor - outer_layer_height)
                    diff_original = abs(current_layer_height - outer_layer_height)
                    
                    # Choose the option that gets us closest to outer_layer_height
                    if diff_original <= diff_ceil and diff_original <= diff_floor:
                        # Keep original if it's closest to desired height
                        passes_needed = 1
                        height_per_pass = current_layer_height
                    elif diff_ceil < diff_floor:
                        passes_needed = passes_ceil
                        height_per_pass = height_per_pass_ceil
                    else:
                        passes_needed = passes_floor
                        height_per_pass = height_per_pass_floor
                    
                    extrusion_multiplier = 1.0 / passes_needed
                    
                    logging.info(f"Layer {current_layer}: Z={current_z:.4f}, layer_height={current_layer_height:.4f}mm, "
                               f"target_height={outer_layer_height:.4f}mm\n"
                               f"    Options: ceil={height_per_pass_ceil:.4f}mm/pass ({passes_ceil} passes), "
                               f"floor={height_per_pass_floor:.4f}mm/pass ({passes_floor} passes)\n"
                               f"    Chosen: {passes_needed} passes at {height_per_pass:.4f}mm/pass "
                               f"(diff={min(diff_original, diff_ceil, diff_floor):.4f}mm)")
                else:
                    # When adaptive layer is thinner, use single pass with adjusted extrusion
                    passes_needed = 1
                    height_per_pass = current_layer_height
                    extrusion_multiplier = 1
                    
                    logging.info(f"Layer {current_layer}: Z={current_z:.4f}, layer_height={current_layer_height:.4f}mm, "
                               f"target_height={outer_layer_height:.4f}mm\n"
                               f"    Thin layer: single pass with adjusted extrusion ({extrusion_multiplier:.4f}x)")

                # Find the starting position from the last G1 move
                start_pos = None
                for j in range(i - len(external_block_lines) - 1, max(0, i - len(external_block_lines) - 10), -1):
                    line = lines[j]
                    if "G1" in line and "X" in line and "Y" in line:
                        x_match = re.search(r'X([-\d.]+)', line)
                        y_match = re.search(r'Y([-\d.]+)', line)
                        if x_match and y_match:
                            start_pos = (float(x_match.group(1)), float(y_match.group(1)))
                            break

                # Generate passes
                for pass_num in range(passes_needed):
                    # Calculate Z height for this pass
                    if passes_needed == 1:
                        # For single pass, use the original Z height
                        pass_z = current_z
                    else:
                        # For multiple passes, distribute height
                        pass_z = (current_z - current_layer_height) + ((pass_num + 1) * height_per_pass)
                    
                    logging.info(f"    Pass {pass_num + 1}: Z={pass_z:.4f}")
                    
                    # Add travel move back to start position (except for first pass)
                    if pass_num > 0 and start_pos:
                        modified_lines.append(f"G1 X{start_pos[0]:.3f} Y{start_pos[1]:.3f} F9000 ; Travel back to start\n")
                    
                    # Set Z height for this pass
                    modified_lines.append(f"G1 Z{pass_z:.3f} ; Pass {pass_num + 1} of {passes_needed}\n")
                    
                    # Process extrusion lines
                    for block_line in external_block_lines:
                        if "G1" in block_line and "E" in block_line:
                            e_match = re.search(r'E([-\d.]+)', block_line)
                            if e_match:
                                e_value = float(e_match.group(1))
                                new_e_value = e_value * extrusion_multiplier
                                modified_line = re.sub(r'E[-\d.]+', f'E{new_e_value:.5f}', block_line)
                                modified_lines.append(modified_line)
                        else:
                            modified_lines.append(block_line)
        else:
            modified_lines.append(line)
            i += 1

    # Overwrite the input file with the modified G-code
    with open(input_file, 'w') as outfile:
        outfile.writelines(modified_lines)

    logging.info("G-code processing completed")
    logging.info(f"Log file saved at {log_file_path}")

# Main execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process G-code file to modify external perimeter printing.')
    parser.add_argument('input_file', help='Input G-code file')
    parser.add_argument('-outerLayerHeight', '--outer-layer-height', type=float,
                       help='Desired height for outer walls (mm). If not provided, will use min_layer_height from G-code')
    
    args = parser.parse_args()
    
    process_gcode(input_file=args.input_file, outer_layer_height=args.outer_layer_height)

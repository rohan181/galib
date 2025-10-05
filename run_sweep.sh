#!/bin/bash
# run_sweep.sh
# Automated parameter sweep script for Adventure World
# Runs multiple simulations with different spawn rates

echo "========================================"
echo "Adventure World - Automated Parameter Sweep"
echo "========================================"
echo ""

# Create output directory
mkdir -p sweep_results

# Array of spawn rates to test
spawn_rates=(0.1 0.2 0.3 0.4 0.5)

echo "Testing spawn rates: ${spawn_rates[@]}"
echo ""

# Loop through each spawn rate
for rate in "${spawn_rates[@]}"
do
    echo "----------------------------------------"
    echo "Running simulation with spawn rate: $rate"
    echo "----------------------------------------"
    
    # Create temporary parameter file
    cat > params_temp.csv << EOF
# Temporary parameter file
max_timesteps, 300
spawn_rate, $rate
EOF
    
    # Run simulation and save output
    output_file="sweep_results/results_rate_${rate}.txt"
    python3 adventureworld.py -f map1.csv -p params_temp.csv > "$output_file"
    
    echo "Results saved to: $output_file"
    echo ""
done

# Clean up temporary file
rm params_temp.csv

echo "========================================"
echo "Parameter sweep complete!"
echo "========================================"
echo ""
echo "Results are in the 'sweep_results' directory:"
ls -lh sweep_results/
echo ""
echo "To analyze results, check each output file."
#!/usr/bin/env python3
"""
Command Line Interface (CLI) for PyMudCement-Optima

This module provides a terminal-based interface for using PyMudCement-Optima
when Streamlit is not available.
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.engineering_calculators import HydrostaticPressureCalculator
from src.core.models import Formation


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PyMudCement-Optima - Drilling Engineering Calculator"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Pressure balance command
    pressure_parser = subparsers.add_parser(
        "pressure-balance", help="Calculate pressure balance"
    )
    pressure_parser.add_argument("--depth", type=float, required=True,
                                 help="Depth (m)")
    pressure_parser.add_argument("--pore-pressure", type=float, required=True,
                                 help="Pore pressure (Pa)")
    pressure_parser.add_argument("--fracture-gradient", type=float, required=True,
                                 help="Fracture gradient (Pa/m)")
    
    args = parser.parse_args()
    
    if args.command == "pressure-balance":
        formation = Formation(
            name="Custom Interval",
            depth_m=args.depth,
            pore_pressure_pa=args.pore_pressure,
            fracture_gradient=args.fracture_gradient,
        )
        
        required_density, required_ppg = (
            HydrostaticPressureCalculator.calculate_mud_weight_for_pore_balance(
                formation
            )
        )
        
        print(f"\n=== Pressure Balance Analysis ===")
        print(f"Depth: {formation.depth_m} m")
        print(f"Pore Pressure: {formation.pore_pressure_pa/1e6:.2f} MPa")
        print(f"Fracture Gradient: {formation.fracture_gradient} Pa/m")
        print(f"\nRequired Mud Density: {required_density:.3f} kg/m³")
        print(f"Required Mud Weight: {required_ppg:.3f} ppg")
        
        safety_check = HydrostaticPressureCalculator.evaluate_safety_window(
            required_density,
            formation.pore_pressure_pa,
            formation.fracture_gradient,
            formation.depth_m
        )
        
        print(f"\nSafety Status: {safety_check['safety_status']}")
        print(f"Pore Pressure Limit: {safety_check['pore_pressure_limit']:.3f} kg/m³")
        print(f"Fracture Pressure Limit: {safety_check['fracture_pressure_limit']:.3f} kg/m³")


if __name__ == "__main__":
    main()

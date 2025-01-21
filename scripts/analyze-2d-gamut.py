#!/usr/bin/env python3
#./analyze-2d-gamut.py --inputcsv=test-data.csv --reference=ntsc --output=analysis.jpg
import argparse
import sys
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import matplotlib
from matplotlib.patches import Polygon
from shapely.geometry import Polygon as ShapelyPolygon
import colour
from colour.plotting import plot_chromaticity_diagram_CIE1931

REFERENCE_GAMUTS = {
    'ntsc': {
        'primaries': np.array([[0.67, 0.33], [0.21, 0.71], [0.14, 0.08]]),
        'white': np.array([0.3101, 0.3162]),  # CIE Illuminant C
        'label': 'NTSC 1953'
    },
    'srgb': {
        'primaries': np.array([[0.64, 0.33], [0.30, 0.60], [0.15, 0.06]]),
        'white': np.array([0.3127, 0.3290]),  # D65
        'label': 'sRGB'
    },
    'dcip3': {
        'primaries': np.array([[0.68, 0.32], [0.265, 0.69], [0.15, 0.06]]),
        'white': np.array([0.314, 0.351]),    # DCI White
        'label': 'DCI-P3'
    },
    'rec709': {
        'primaries': np.array([[0.64, 0.33], [0.30, 0.60], [0.15, 0.06]]),
        'white': np.array([0.3127, 0.3290]),  # D65
        'label': 'Rec.709'
    },
    'rec2020': {
        'primaries': np.array([[0.708, 0.292], [0.170, 0.797], [0.131, 0.046]]),
        'white': np.array([0.3127, 0.3290]),  # D65
        'label': 'Rec.2020'
    }
}

def validate_xy_coordinates(x, y):
    """Validate if xy coordinates are within valid chromaticity range"""
    try:
        x = float(x)
        y = float(y)
        if not (0 <= x <= 1 and 0 <= y <= 1 and x + y <= 1):
            raise ValueError(f"Invalid chromaticity coordinates: x={x}, y={y}")
        return True
    except (ValueError, TypeError):
        raise ValueError(f"Invalid coordinate values: x={x}, y={y}")

def calculate_area(points):
    """Calculate polygon area using shoelace formula"""
    # Convert points to list of tuples for easy comparison
    points = [(float(p[0]), float(p[1])) for p in points]
    
    # Close the polygon if not already closed
    if points[0] != points[-1]:
        points.append(points[0])
    
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    
    return 0.5 * abs(sum(i * j for i, j in zip(x, y[1:] + y[:1])) - 
                    sum(i * j for i, j in zip(x[1:] + x[:1], y)))

def process_measurements(df):
    """Process and validate measurement data"""
    required_colors = {'R', 'G', 'B', 'W'}
    measured_colors = set(df['Color'])
    
    if not required_colors.issubset(measured_colors):
        missing = required_colors - measured_colors
        raise ValueError(f"Missing measurements for: {missing}")
    
    measured = {}
    for _, row in df.iterrows():
        try:
            x, y = float(row.x), float(row.y)
            validate_xy_coordinates(x, y)
            measured[row.Color] = (x, y)  # Store as tuple
        except ValueError as e:
            raise ValueError(f"Invalid measurement for {row.Color}: {e}")
    
    return measured

def main():
    parser = argparse.ArgumentParser(description='Color Gamut Analyzer')
    parser.add_argument('--inputcsv', required=True, help='Measurement CSV file')
    parser.add_argument('--reference', required=True, 
                       choices=REFERENCE_GAMUTS.keys(), help='Reference standard')
    parser.add_argument('--output', help='Output plot filename (jpg/png/pdf)')
    args = parser.parse_args()

    try:
        # Set backend based on mode
        if args.output:
            matplotlib.use('Agg')
        else:
            matplotlib.use('TkAgg')
        
        # Load and validate data
        df = pd.read_csv(args.inputcsv)
        required_columns = {'Color', 'x', 'y'}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"CSV must contain columns: {required_columns}")
        
        # Process measurements
        measured = process_measurements(df)
        ref = REFERENCE_GAMUTS[args.reference]
        
        # Create figure
        plt.close('all')
        fig = plt.figure(figsize=(10, 10))
        
        # Plot CIE diagram
        plot_chromaticity_diagram_CIE1931(
            axes=plt.gca(),
            show=False,
            title=False
        )
        ax = plt.gca()
        
        # Prepare polygon points
        m_points = [(float(measured[c][0]), float(measured[c][1])) for c in ['R', 'G', 'B']]
        r_points = [(float(p[0]), float(p[1])) for p in ref['primaries']]

        # Calculate areas
        m_area = calculate_area(m_points)
        r_area = calculate_area(r_points)
        
        # Calculate coverage
        poly1 = ShapelyPolygon(m_points)
        poly2 = ShapelyPolygon(r_points)
        overlap = poly1.intersection(poly2)
        coverage = overlap.area / r_area * 100 if not overlap.is_empty else 0
        relative_area = (m_area / r_area) * 100

        # Calculate white point differences
        w_measured = measured['W']
        w_reference = ref['white']
        delta_x = w_measured[0] - w_reference[0]
        delta_y = w_measured[1] - w_reference[1]

        # Plot measured gamut
        ax.add_patch(Polygon(
            m_points, closed=True, fill=False,
            edgecolor='black', linewidth=2,
            label=f'Measured ({m_area:.3f})'
        ))

        # Plot reference gamut
        ax.add_patch(Polygon(
            r_points, closed=True, fill=False,
            edgecolor='white', linewidth=2, linestyle='--',
            label=f'{ref["label"]} ({r_area:.3f})'
        ))

        # Plot white points
        ax.plot(w_measured[0], w_measured[1], 'bo', markersize=10,
               label=f'Measured White ({w_measured[0]:.3f}, {w_measured[1]:.3f})')
        ax.plot(w_reference[0], w_reference[1], 'rx', markersize=10,
               label=f'Reference White ({w_reference[0]:.3f}, {w_reference[1]:.3f})')

        # Add info box
        info_text = (f'Coverage: {coverage:.1f}%\n'
                    f'Overlap Area: {overlap.area:.3f}\n'
                    f'Relative Area: {relative_area:.1f}%\n'
                    f'White Point Δx: {delta_x:+.4f}\n'
                    f'White Point Δy: {delta_y:+.4f}')
        plt.text(0.02, 0.98,
                info_text,
                transform=ax.transAxes, fontsize=10,
                bbox=dict(facecolor='white', alpha=0.8),
                verticalalignment='top')

        # Finalize plot
        ax.legend(loc='upper right', bbox_to_anchor=(1.0, 1.0))
        plt.title('Color Gamut Analysis on CIE 1931 Diagram')
        plt.tight_layout()

        # Save or show plot
        if args.output:
            plt.savefig(args.output, bbox_inches='tight', dpi=300)
        else:
            plt.show()
        plt.close(fig)

        # Print numerical results
        print("\nNumerical Analysis:")
        print(f"Reference Gamut: {ref['label']}")
        print(f"Measured Gamut Area: {m_area:.6f}")
        print(f"Reference Gamut Area: {r_area:.6f}")
        print(f"Overlap Area: {overlap.area:.6f}")
        print(f"Coverage: {coverage:.1f}%")
        print(f"Relative Area: {relative_area:.1f}%")
        print("\nWhite Point Analysis:")
        print(f"Measured White: ({w_measured[0]:.4f}, {w_measured[1]:.4f})")
        print(f"Reference White: ({w_reference[0]:.4f}, {w_reference[1]:.4f})")
        print(f"Δx: {delta_x:+.4f}")
        print(f"Δy: {delta_y:+.4f}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        plt.close('all')
        sys.exit(1)

if __name__ == '__main__':
    main()

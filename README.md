# imagetools

**imagetools** is a collection of Python scripts for analyzing display performance based on xy color coordinates.

## How to Use This Repository

### 1. Clone the Repository
```sh
git clone https://github.com/hackboxguy/imagetools.git
cd imagetools
mkdir data
cp /your/display/measurements.csv data/
```

### 2. Prepare Your Measurement Data
Ensure that `measurements.csv` follows this format e.g:

```
Color,x,y
R,0.6927,0.3010
G,0.2818,0.6890
B,0.1507,0.0613
W,0.2915,0.3004
```

Before running the Docker command, place your CSV files inside the local `./data` folder (to be mounted as a volume).

---

## Analyzing Display Color Gamut

To visualize the measured color gamut of a display compared to the **NTSC reference gamut**, run the docker-container as:

```sh
docker run --rm -v $(pwd)/data:/data hackboxguy/imagetools analyze-2d-gamut.py \
  --inputcsv=/data/measurements.csv --reference=ntsc --output=/data/ntsc-compare.jpg \
  --title="Display Masurement compared with NTSC"
```

This command generates an image (`ntsc-compare.jpg`) in local ```./data``` folder that:
- Plots the **measured color gamut** along with the **NTSC reference gamut** on a 2D chromaticity diagram.
- Marks the **D65 white point**.
- Displays the **relative area and coverage area** of the measured gamut compared to NTSC.

### Supported Reference Gamuts
Apart from NTSC, this script allows comparisons with:
- **sRGB** ```srgb```
- **DCI-P3** ```dcip3```
- **REC.2020** ```rec2020```

---

## Checking White Point Tolerance

To check if the measured **white point** falls within a **specified tolerance** of the NTSC D65 reference white point, use:

```sh
docker run --rm -v $(pwd)/data:/data hackboxguy/imagetools analyze-2d-gamut.py \
  --inputcsv=/data/measurements.csv --reference=ntsc --output=/data/ntsc-compare.jpg --whitepointtol=0.01
```

This will indicate whether the measured white point is within the **reference white point ellipse**.

---

## Comparing Cold vs Warm Display Gamut

To compare the **initial (cold) color gamut** with **warm display measurements** and a **reference gamut**, use:

```sh
docker run --rm -v $(pwd)/data:/data hackboxguy/imagetools analyze-2d-gamut.py \
  --inputcsvcold=/data/cold-meas.csv --inputcsv=/data/warm-meas.csv --reference=ntsc \
  --output=/data/ntsc-compare-warm-cold-gamut.jpg \
  --title="Comparison of Cold and Warm Gamut with NTSC"
```

### Example Outputs

#### Cold vs Warm Gamut Comparison
![NTSC Gamut Comparison](/images/ntsc-compare-warm-cold-gamut.jpg)

#### White Point Tolerance Visualization
![White Point Tolerance](/images/white-point-tolerance.jpg)

#### Warm Gamut Comparison with NTSC/DCI-P3/sRGB/REC2020(all images stitched together)
![All Comparison](/images/compare-all.jpg)

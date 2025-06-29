Decide: Decision Tree-Based Inventory Data Estimation Tool
Overview
Decide is a Python-based tool designed to assist Life Cycle Assessment (LCA) practitioners in generating preliminary estimates of inventory data for chemical processes. It uses decision tree models to predict process characteristics based on reaction and molecular property inputs.

Note: The estimates provided by DecIDE are intended for screening purposes only. Users should replace these estimates with actual plant data or detailed process simulations as soon as feasible.

This tool is provided as part of the Electronic Supplementary Information for the publication: 
Tim Langhorst, Benedikt Winter, Moritz Tuchschmid, Dennis Roskosch, André Bardow, From reaction stoichiometry to life cycle assessment: Decision tree-based estimation tool, ACS Environmental Au, 2025

Features
Estimates inventory data using decision tree models

Supports both manual and automated input via the DIPPR801 database

Outputs estimated values along with mean absolute error (MAE) of the prediction

Inputs
Reaction stoichiometry

Thermo-physical properties of reactants and products (e.g., boiling points, molecular weights)

Outputs
Estimated inventory parameters for each reaction

Associated MAE of the prediction (based on training data in the same decision tree leaf)

Installation
Clone the repository (or download the code files).

Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
Install the required Python packages:


pip install -r requirements.txt
Getting Started
For a visual walkthrough, refer to the accompanying Visual_Guide.pdf.

1. Prepare Input Data (Input.xlsx)
You have two options for providing input:

Option A: Using the DIPPR801 Database (.accdb)
Fill out the second sheet (Input_autom):

Provide CAS Numbers and stoichiometric coefficients

Include:

Number: Unique identifier for the reaction

Name: Descriptive name (e.g., main product name)

Copy the Number and Name to the first sheet (Input_manual) — this is required for autofill to function properly.

Place the .accdb database file into the DIPPR/ folder.

The code will automatically retrieve missing molecular data from the DIPPR database.

Option B: Manual Input Only (No DIPPR Access)
Fill out the first sheet (Input_manual):

Number: Unique reaction ID

Name: Descriptive name

F, N, Cl, C, c: Atomic composition (see cell notes for guidance)

countPro: Number of unique products

Boiling Points (BP): Max/min boiling points for reactants (E) and products (P)

MW_mainP: Molecular weight of the main product (g/mol)

AddSidePro: Enter 0 (no expected side products) or 1 (if you expect side product separation)

stoichioH2: Moles of hydrogen required as a reactant

water: Stoichiometric coefficient for water (if by-product)

x_MP: Molar fraction of the main product among total products

Tip: Try both AddSidePro = 0 and 1 for sensitivity analysis.

2. Run the Tool
Launch Decide.py in your Python environment.

The tool will automatically:

Fill in missing data from DIPPR (if applicable)

Update the input file

Generate output with estimated inventory data

Output
The output file will include:

Estimated inventory values

Mean Absolute Error (MAE) for each prediction (based on decision tree leaf statistics)

License
This work is published under the MIT Licence:
Copyright (c) 2025 Tim Langhorst

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
The original publication* should be cited.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


*This tool is part of the Electronic Supplementary Information of the following publication:
Tim Langhorst, Benedikt Winter, Moritz Tuchschmid, Dennis Roskosch, André Bardow, From reaction stoichiometry to life cycle assessment: Decision tree-based estimation tool, ACS Environmental Au, 2025

This tool uses functions of the following tools published under BSD 3-Clause License:
Scikit-learn:
Copyright (c) 2007-2024 The scikit-learn developers.
Pandas:
Copyright (c) 2008-2011, AQR Capital Management, LLC, Lambda Foundry, Inc. and PyData Development Team
Copyright (c) 2011-2023, Open source contributors.
Numpy:
Copyright (c) 2005-2024, NumPy Developers.

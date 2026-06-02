# Karonga OHDSI GIS Pipeline

## Overview

This repository contains a metadata-driven climate-health research pipeline developed for the Karonga Health and Demographic Surveillance System (HDSS) in Malawi.

The project integrates climate exposures with mortality surveillance data using:

* GaiaCatalog
* gaiaCore
* gaiaDB
* OMOP Common Data Model (CDM)
* OHDSI GIS Extension (EXTERNAL_EXPOSURE)

The objective is to develop a reusable and standardized workflow for deriving environmental exposure variables that can be integrated with health data for climate-health research.

---

## Research Use Case

### Research Question

Are flood-related environmental exposures associated with increased infectious disease mortality in the Karonga HDSS population?

### Outcomes of Interest

* Diarrhoeal disease mortality
* Malaria mortality
* Acute respiratory infection mortality

### Environmental Exposure Variables

* Flood event count
* Flood intensity
* Flood duration
* Lagged flood exposure indicators
* Climate summaries

---

## Project Architecture

The pipeline consists of two complementary workflows.

### 1. Clinical Workflow (Traditional OHDSI)

```text
HDSS Verbal Autopsy Data
        ↓
ICD-10 Coding
        ↓
ATHENA Vocabulary Mapping
        ↓
OMOP CDM
        ↓
OHDSI Analytics
```

### 2. Exposure Workflow (Novel Component)

```text
ERA5 Climate Data
        ↓
GaiaCatalog Metadata Registration
        ↓
Automated Retrieval
        ↓
Exposure Engineering
        ↓
Backbone Tables
        ↓
OMOP EXTERNAL_EXPOSURE
        ↓
OHDSI Analytics
```

The exposure workflow is metadata-driven and designed to support reusable environmental exposure pipelines.

---

## Current Progress

### Metadata Registration

The following have been registered in GaiaCore backbone tables:

#### Dataset Registration

* ERA5 Climate Dataset

#### Variable Registration

* Total precipitation
* 2m temperature
* 2m dewpoint temperature
* 10m u-component of wind
* 10m v-component of wind

#### Spatial Registration

* Karonga HDSS study geometry

#### Temporal Registration

* Study period (2015–2021)

---

### Automated Retrieval

Implemented a metadata-driven retrieval pipeline that:

* Reads metadata from GaiaCore backbone tables
* Retrieves ERA5 hourly climate data from Copernicus Climate Data Store (CDS)
* Extracts data for the Karonga HDSS bounding box
* Stores raw climate data for downstream processing

---

### Exposure Engineering

Implemented climate processing workflows to generate:

* Flood event count
* Flood intensity
* Flood duration
* Lagged exposure indicators
* Monthly climate summaries

---

### Backbone Integration

Generated exposure datasets have been:

* Loaded into `backbone.attr_template`
* Registered in `backbone.variable_source`
* Linked to study geometry and temporal coverage

This creates a metadata-driven chain connecting:

```text
Dataset
   ↓
Variables
   ↓
Geometry
   ↓
Temporal Coverage
   ↓
Derived Exposures
   ↓
attr_template
```

---

## Repository Structure

```text
karonga-ohdsi-gis-pipeline/

├── metadata/
│   ├── jsonld/
│   └── etl/
│
├── etl/
│   ├── retrieval/
│   ├── processing/
│   ├── loading/
│   └── utils/
│
├── sql/
│
├── raw/
│   ├── era5/
│   ├── era5_land/
│   ├── flood_hazard/
│   ├── hydrorivers/
│   └── sdoh/
│
├── processed/
│   ├── climate/
│   ├── hydrology/
│   └── external_exposure/
│
├── notebooks/
│
├── docker/
│
├── requirements.txt
├── README.md
└── .gitignore
```

### Workflow Mapping

| Stage                    | Location            |
| ------------------------ | ------------------- |
| Metadata Registration    | `metadata/`, `sql/` |
| Data Retrieval           | `etl/retrieval/`    |
| Exposure Processing      | `etl/processing/`   |
| Backbone Loading         | `etl/loading/`      |
| Raw Data Storage         | `raw/`              |
| Processed Outputs        | `processed/`        |
| Validation & Exploration | `notebooks/`        |

---

## Data Sources

### ERA5 Climate Data (Copernicus CDS)

Currently implemented:

* Total precipitation
* 2m temperature
* 2m dewpoint temperature
* 10m wind components

These variables are used to derive flood-related exposure indicators and climate summaries.

---

## Standards Alignment

This project aligns with:

* OHDSI GIS Working Group
* OMOP Common Data Model (CDM)
* OMOP EXTERNAL_EXPOSURE
* GaiaCatalog
* gaiaCore
* FAIR Principles
* CDIF4EOSC
* I-ADOPT Variable Framework
* Essential Variables (EV) discussions within RDA

---

## Next Steps

The same metadata-driven workflow will be applied to additional environmental datasets.

### ERA5-Land Hydrological Variables

Register and process:

* Surface runoff
* Soil moisture

### Social Determinants of Health (SDoH)

Register and integrate:

* Sanitation indicators
* Housing quality indicators
* Water access indicators

### Flood Hazard Layers

Register and process:

* Flood susceptibility maps
* Flood risk zones
* Flood extent datasets

### HydroRIVERS

Register and integrate:

* River networks
* Distance-to-river exposures
* Catchment-based exposure metrics

---

## Long-Term Goal

Develop a reusable metadata-driven workflow where environmental datasets are:

1. Registered in GaiaCore backbone tables
2. Retrieved automatically
3. Processed into standardized exposure indicators
4. Loaded into backbone exposure tables
5. Integrated into OMOP EXTERNAL_EXPOSURE
6. Analysed using OHDSI tools

The workflow is designed to support climate-health research across multiple HDSS sites and environmental datasets.

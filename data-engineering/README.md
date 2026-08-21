# DisasterLens AI - Data Engineering



## PURPOSE



The Data Engineering component collects, validates, cleans, normalizes, and prepares disaster-related reports for the AI/ML pipeline.



The current MVP supports both:



* Demo disaster reports

* Live earthquake data from the USGS API



---



## PIPELINE



```text

Source

  |

  v

Ingestion

  |

  v

Validation

  |

  v

Cleaning

  |

  v

Normalization

  |

  v

Deduplication

  |

  v

Keyword Pre-filter

  |

  v

AI Input

  |

  v

Validation

```



---



## CURRENT MVP



The system currently performs:



* Data ingestion

* Required-field validation

* Timestamp validation

* Text cleaning

* Source normalization

* Duplicate detection

* Disaster keyword pre-filter

* Repeated-letter normalization for keyword matching

* USGS earthquake API ingestion

* USGS data normalization

* Magnitude extraction

* Location and coordinate extraction

* AI input generation

* Data-quality metrics

* AI input validation



---



## DATA SOURCES



### Demo Data



```text

data/raw/demo_reports.json

```



### USGS Earthquake Data



The project uses the USGS earthquake feed:



```text

https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson

```



The USGS data is fetched automatically by:



```text

ingestion_usgs.py

```



---



## OUTPUTS



Processed reports:



```text

data/processed/processed_reports.json

```



AI-ready reports:



```text

data/processed/ai_input.json

```



Data-quality metrics:



```text

data/processed/data_quality.json

```



Raw normalized USGS reports:



```text

data/raw/usgs_reports.json

```



---



## PROJECT FILES



```text

disasterlens-data/

|

|-- ingestion.py

|-- ingestion_usgs.py

|-- run_pipeline.py

|-- test_ai_input.py

|-- README.md

|

|-- data/

    |

    |-- raw/

    |   |-- demo_reports.json

    |   |-- usgs_reports.json

    |

    |-- processed/

        |-- processed_reports.json

        |-- ai_input.json

        |-- data_quality.json

```



---



## RUN THE COMPLETE PIPELINE



The recommended way to run the system is:



```cmd

python run_pipeline.py

```



This automatically performs:



1. USGS data ingestion

2. Data processing

3. AI input validation



---



## RUN INDIVIDUAL COMPONENTS



### USGS ingestion



```cmd

python ingestion_usgs.py

```



### Data processing



```cmd

python ingestion.py

```



### AI input validation



```cmd

python test_ai_input.py

```



### Complete pipeline



```cmd

python run_pipeline.py

```



---



## DATA QUALITY



The pipeline reports:



* Reports received

* Valid reports

* Duplicate reports

* Reports sent to AI

* Processed reports



Example:



```text

========== PIPELINE METRICS ==========

Reports received: 12

Valid reports: 11

Duplicates: 1

Sent to AI: 7

Processed reports: 10

=======================================

```



---



## IMPORTANT



The keyword filter is only a **pre-filter**.



A keyword match does not prove that a disaster has occurred.



For example, a report containing the word `earthquake` is only selected for further processing. The AI/ML system should perform the actual disaster classification.



---



## TRACEABILITY



Raw source information is preserved for debugging and traceability.



USGS records retain:



* Source

* Source ID

* Original text

* Magnitude

* Timestamp

* URL

* Location

* Latitude

* Longitude



---



## CURRENT STATUS



The Data Engineering MVP is operational.



The complete pipeline has been tested successfully with live USGS data:



```text

USGS INGESTION          PASSED

DATA PROCESSING         PASSED

USGS VALIDATION         PASSED

AI INPUT VALIDATION     PASSED

MASTER PIPELINE         PASSED

```



The system is ready for the next stage of the DisasterLens AI project.




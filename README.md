# Systematic Literature Review Metadata Curation Pipeline

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-Active-success.svg)

A comprehensive **Robotic Process Automation (RPA)** pipeline for curating systematic literature review datasets to enable Large Language Model (LLM) automation of article selection tasks.

## Project Overview

This project addresses a critical challenge in systematic literature reviews: the time-intensive manual process of article selection and metadata curation. Traditional systematic reviews can take 1-3 years and require reviewing thousands of articles. Our solution creates high-quality annotated datasets from published systematic reviews using automated metadata extraction techniques.

### Project Results

- **16 systematic review datasets** processed and curated
- **32,614 total articles** with extracted metadata  
- **99% article recovery rate** from academic databases
- **97% automation success rate** for metadata extraction
- **8 academic database sources** integrated

### Research Impact

The curated datasets enable researchers to train and evaluate LLMs for automating systematic review processes, potentially reducing review time from years to weeks while maintaining scientific rigor.

## Architecture

### Technical Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Web Automation** | Selenium WebDriver | Browser automation and navigation |
| **HTML Parsing** | BeautifulSoup4 | Content extraction and parsing |
| **Bibliography Processing** | Pybtex | BibTeX format handling |
| **Data Processing** | Pandas | Data manipulation and analysis |
| **Text Processing** | NLTK | Natural language processing |
| **Cross-platform Support** | Python 3.8+ | Windows and Linux compatibility |

### Project Structure

```
Scripts/
├── core/                   # Core infrastructure
│   ├── SRProject.py       # Base systematic review class
│   ├── os_path.py         # Cross-platform path management
│   └── __init__.py
├── datasets/              # Individual dataset processors (16 datasets)
│   ├── ArchiML.py         # Architecture & Machine Learning (2,766 articles)
│   ├── CodeClone.py       # Code Clone Detection (10,454 articles)
│   ├── GameSE.py          # Game Software Engineering (1,520 articles)
│   ├── ModelingAssist.py  # Modeling Assistance (3,002 articles)
│   └── ... (12 more datasets)
├── extraction/            # Metadata extraction pipeline
│   ├── findMissingMetadata.py  # Core extraction logic
│   ├── webScraping.py         # Selenium-based scraping
│   ├── htmlParser.py          # HTML content parsing
│   └── searchInSource.py      # Source-specific search
├── specialized/           # Specialized processors
│   ├── GameSE_abstract.py     # Abstract-level analysis
│   ├── GameSE_title.py        # Title-level analysis
│   └── Demo.py, IFT3710.py    # Course-specific demos
├── utilities/             # Helper scripts
│   ├── convert_encoding.py    # Character encoding conversion
│   ├── get_non_matching_titles.py  # Quality control
│   └── rename_html.py         # File management
├── data/                  # Data files and caches
├── testing/               # Test scripts
├── logs/                  # Log files and documentation
└── main.py               # Main pipeline entry point
```

## Getting Started

### Prerequisites

- **Python 3.8+** with pip
- **Firefox browser** (for Selenium WebDriver)
- **Academic database access** (institutional subscriptions recommended)
- **Windows 10/11** or **Ubuntu Linux**

### Installation

1. **Clone the repository**
   ```bash
   git clone [repository-url]
   cd "Projet Curation des métadonnées"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure paths**
   - Edit `Scripts/core/os_path.py` for your system paths
   - Ensure Firefox and geckodriver are properly installed

### Quick Start

```bash
# Process a single dataset
python Scripts/main.py ArchiML

# Process multiple datasets
python Scripts/main.py CodeClone ModelingAssist GameSE

# Process all default datasets
python Scripts/main.py
```

## Supported Datasets

| Dataset | Domain | Articles | Status | Description |
|---------|---------|----------|---------|-------------|
| **ArchiML** | ML Architecture | 2,766 | Complete | Architecture and Machine Learning integration |
| **CodeClone** | Code Analysis | 10,454 | Complete | Code clone detection and management |
| **CodeCompr** | Code Understanding | 1,508 | Complete | Source code comprehension techniques |
| **GameSE** | Gaming | 1,520 | Complete | Game software engineering practices |
| **ModelingAssist** | Modeling Tools | 3,002 | Complete | Model-driven development assistance |
| **Behave** | Behavioral SE | 1,043 | Complete | Behavioral software engineering |
| **DTCPS** | Cyber-Physical | 4,007 | Complete | Digital twin cyber-physical systems |
| **ESM_2** | Empirical Methods | 1,134 | Complete | Experience sampling methodology |
| **ESPLE** | Empirical SE | 991 | Complete | Empirical software engineering |
| **ModelGuidance** | Model-Driven | 2,105 | Complete | Model-driven development guidance |
| **OODP** | Design Patterns | 1,826 | Complete | Object-oriented design patterns |
| **SecSelfAdapt** | Security | 1,962 | Complete | Security in self-adaptive systems |
| **SmellReprod** | Code Quality | 2,067 | Complete | Code smell reproduction studies |
| **TestNN** | Neural Testing | 2,533 | Complete | Neural network testing approaches |
| **TrustSE** | Trust & Security | 2,564 | Complete | Trust in software engineering |

## Academic Database Support

Our RPA pipeline extracts metadata from 8 major academic databases:

- **[IEEE Xplore](https://ieeexplore.ieee.org/)** - Technical publications and conferences
- **[ACM Digital Library](https://dl.acm.org/)** - Computing and information technology  
- **[ScienceDirect](https://www.sciencedirect.com/)** - Elsevier's multidisciplinary publications
- **[SpringerLink](https://link.springer.com/)** - Academic books and journals
- **[Scopus](https://www.scopus.com/search/form.uri?display=basic&zone=header&origin=recordpage#basic)** - Citation and abstract database
- **[Web of Science](https://www.webofscience.com/wos/woscc/basic-search)** - Multidisciplinary citation database
- **[arXiv](https://arxiv.org/)** - Preprint repository for STEM fields
- **[PubMed Central](https://pubmed.ncbi.nlm.nih.gov/)** - Biomedical literature archive

## Configuration

### Key Parameters in `main.py`

```python
# Enable/disable metadata extraction
do_extraction = True  # Set to False for testing without web scraping

# Process specific datasets
args = ['ArchiML', 'CodeClone', 'ModelingAssist']

# Run identifier for batch processing  
run = 999
```

### Path Configuration

Edit `Scripts/core/os_path.py` for your environment:

```python
# Main project path
MAIN_PATH = "C:\\Users\\...\\Projet Curation des métadonnées"

# Extracted content cache
EXTRACTED_PATH = "C:\\Users\\...\\Database"
```

## Data Schema

All datasets follow this standardized schema:

### Core Metadata Fields
| Field | Type | Description |
|-------|------|-------------|
| `key` | String | Unique article identifier |
| `project` | String | Dataset name |
| `title` | String | Article title |
| `abstract` | String | Article abstract |
| `keywords` | String | Article keywords (semicolon-separated) |
| `authors` | String | Author list (semicolon-separated) |
| `venue` | String | Publication venue |
| `doi` | String | Digital Object Identifier |

### Review Process Fields
| Field | Type | Description |
|-------|------|-------------|
| `screened_decision` | String | Initial screening decision |
| `final_decision` | String | Final inclusion decision |
| `mode` | String | Review mode (new_screen, snowballing) |
| `inclusion_criteria` | String | Inclusion criteria description |
| `exclusion_criteria` | String | Exclusion criteria description |
| `reviewer_count` | Integer | Number of reviewers |

### Technical Fields
| Field | Type | Description |
|-------|------|-------------|
| `source` | String | Academic database source |
| `year` | String | Publication year |
| `meta_title` | String | Source dataset title |
| `link` | String | Source URL |
| `publisher` | String | Publisher information |
| `metadata_missing` | String | Missing metadata indicators |

## Processing Pipeline

### 1. **Dataset Loading**
```python
# Load systematic review dataset
sr_project = ArchiML()  # Example dataset
```

### 2. **Preprocessing**
- Duplicate title detection and resolution
- Data schema normalization
- Character encoding standardization

### 3. **Metadata Extraction** (Optional)
```python
# Enable web scraping
do_extraction = True
completed_df = findMissingMetadata.main(sr_project.df, do_extraction, run, dataset_name)
```

### 4. **Data Cleaning**
- Unicode character normalization
- Illegal character removal
- Format standardization

### 5. **Quality Assurance**
- Title matching validation
- Missing metadata reporting
- Statistical analysis

### 6. **Export**
```python
# Export to TSV format
ExportToCSV(sr_project)
```

## Development

### Adding New Datasets

1. **Create dataset class** in `Scripts/datasets/`
```python
class NewDataset(SRProject):
    def __init__(self):
        super().__init__()
        self.project_name = "NewDataset"
        # Define inclusion/exclusion criteria
        # Set source file paths
```

2. **Add to main.py**
```python
from Scripts.datasets.NewDataset import NewDataset

# Add to main() function
elif arg == "NewDataset":
    sr_project = NewDataset()
```

## Quality Metrics

### Success Rates
- **Article Recovery**: 99% of target articles successfully located
- **Metadata Extraction**: 97% automation success rate
- **Title Matching Accuracy**: >95% using fuzzy matching algorithms

### Validation Techniques
- **Edit distance algorithms** for title similarity
- **Cross-reference verification** when multiple sources available
- **Format standardization** across all datasets
- **Comprehensive error logging** for manual review

## Academic Context

This project supports research in:
- **Systematic Literature Review Automation**
- **Large Language Model Training for Academic Tasks**
- **Robotic Process Automation in Research**

---

**Note**: This pipeline requires academic database access and appropriate institutional subscriptions for optimal functionality. The system is designed for research and educational purposes.
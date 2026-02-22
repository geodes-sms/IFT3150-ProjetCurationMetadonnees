# Systematic Literature Review Metadata Curation Pipeline

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-Active-success.svg)

A comprehensive **Robotic Process Automation (RPA)** pipeline for curating systematic literature review datasets to enable Large Language Model (LLM) automation of article selection tasks.

## Project Overview

This project addresses a critical challenge in systematic literature reviews: the time-intensive manual process of article selection and metadata curation. Traditional systematic reviews can take 1-3 years and require reviewing thousands of articles. Our solution creates high-quality annotated datasets from published systematic reviews using automated metadata extraction techniques.

### Project Results

- **16 systematic review datasets** processed and curated
- **31,548 total articles** with extracted metadata (from 32,646 source records, 1,098 excluded)
- **96.6% article recovery rate** from academic databases
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
│   ├── ArchiML.py         # Architecture & Machine Learning (2,723 articles)
│   ├── CodeClone.py       # Code Clone Detection (9,700 articles)
│   ├── GameSE.py          # Game Software Engineering (3,489 + 1,133 articles)
│   ├── ModelingAssist.py  # Modeling Assistance (2,249 articles)
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

| Dataset | Domain | Articles | Reviewers | SLR Title |
|---------|---------|----------|-----------|-----------|
| **CodeClone** | Code Analysis | 9,700 | -- | A systematic literature review on source code similarity measurement and clone detection: Techniques, applications, and challenges |
| **CodeCompr** | Code Comprehension | 3,930 | -- | A systematic literature review on the impact of formatting elements on code legibility |
| **GameSE-title** | Game SE | 3,489 | 2 | The consolidation of game software engineering: A systematic literature review of software engineering for industry-scale computer games (title screening) |
| **GameSE-abstract** | Game SE | 1,133 | 2 | The consolidation of game software engineering: A systematic literature review of software engineering for industry-scale computer games (abstract screening) |
| **ArchiML** | ML Architecture | 2,723 | 2 | Architecting ML-enabled systems: Challenges, best practices, and design decisions |
| **ModelingAssist** | Modeling Tools | 2,249 | 2 | Understanding the landscape of software modelling assistants: A systematic mapping |
| **ModelGuidance** | Model-Driven | 1,741 | 2 | Modelling guidance in software engineering: A systematic literature review |
| **SmellReprod** | Code Quality | 1,714 | 2 | How far are we from reproducible research on code smell detection? A systematic literature review |
| **SecSelfAdapt** | Security | 1,433 | 2 | A systematic review on security and safety of self-adaptive systems |
| **ESPLE** | Empirical SE | 963 | 2 | Empirical software product line engineering: A systematic literature review |
| **OODP** | Design Patterns | 708 | 2 | A mapping study of language features improving object-oriented design patterns |
| **Behave** | BDD | 590 | 2 | Behaviour driven development: A systematic mapping study |
| **TrustSE** | Trust & Security | 553 | 2 | A systematic literature review on trust in the software ecosystem |
| **DTCPS** | Cyber-Physical | 403 | 2 | Digital-twin-based testing for cyber-physical systems: A systematic literature review |
| **ESM\_2** | Adaptive UI | 114 | 2 | Adaptive user interfaces in systems targeting chronic disease: A systematic literature review |
| **TestNN** | Neural Testing | 105 | 1 | Testing and verification of neural-network-based safety-critical control software: A systematic literature review |
| **Total** | | **31,548** | | |

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
- **Article Recovery**: 96.6% of source records successfully retained (31,548 of 32,646)
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


```markdown
# CSV Reconciliation Tool

A Django-based application for comparing and reconciling differences between two CSV files, with both web interface and CLI support.

## Features

- **CSV Comparison**: Identify missing records and field-level discrepancies
- **Data Normalization**: Handles case differences, whitespace, and date formats
- **Multiple Output Formats**: HTML report and CSV output
- **Dual Interface**: Web UI and command-line tool
- **Configurable**: Ignore specific columns during comparison

## Installation

### Prerequisites
- Python 3.11
- pip

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/csv-reconciliation-tool.git
   cd csv-reconciliation-tool
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate    # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

## Usage

### Web Interface
1. Start the development server:
   ```bash
   python manage.py runserver
   ```

2. Access the web interface at:
   ```
   http://localhost:8000
   ```

### Command Line Interface
```bash
python manage.py csv_reconciler \
  -s source.csv \
  -t target.csv \
  -o report.csv \
  --ignore "column1,column2"
```

Example output:
```
Reconciliation completed:
- Records missing in target: 2
- Records missing in source: 1  
- Records with field discrepancies: 3

Report saved to: report.csv
```

### Sample CSV Format
**source.csv**
```csv
ID,Name,Date,Amount
001,John Doe,2023-01-01,100.00
002,Jane Smith,2023-01-02,200.50
```

**target.csv**  
```csv
ID,Name,Date,Amount
001,John Doe,2023-01-01,100.00
002,Jane Smith,2023-01-04,200.50
003,Robert Brown,2023-01-03,300.00
```

## Testing

Run all tests:
```bash
pytest
```

Key test cases:
- Missing record detection
- Field-level discrepancy identification
- Case-insensitive comparisons
- Date format handling

## Deployment

### Production
Recommended deployment options:
1. **Docker**:
   ```bash
   docker build -t csv-reconciler .
   docker run -p 8000:8000 csv-reconciler
   ```

2. **Heroku**:
   ```bash
   heroku create
   git push heroku main
   ```

### Environment Variables
Set in `.env`:
```
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=.yourdomain.com
```

## Technical Details

### Architecture
```
├── core/              # Business logic
│   ├── reconciler.py  # Core comparison engine
│   └── normalizers.py # Data normalization
├── web/               # Django app
│   ├── views.py       # Web interface
│   └── api.py         # REST API endpoints
└── cli/               # Command line interface
```

### Dependencies
- Django 4.2
- Pandas 2.0
- python-dateutil 2.8

## Contributing

1. Fork the repository
2. Create your feature branch
3. Submit a pull request

## License
MIT
```

Key sections included:
1. Clear installation instructions
2. Usage examples for both interfaces
3. Sample CSV formats
4. Testing methodology
5. Deployment options
6. Architecture overview
7. Contribution guidelines

The README provides everything a developer needs to get started with the project, while also serving as documentation for end users. You can customize the deployment and contributing sections based on your specific requirements.
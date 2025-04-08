
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

###  Video Demonstration

Here is the link to the [Video Demonstration](https://www.loom.com/share/22a2686b27ee4430aa3bb44a50583a7e?sid=d3a76bb2-31e4-4200-a6c3-c4257c757e8f) of the tool in action.



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
└──               # Command line interface
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
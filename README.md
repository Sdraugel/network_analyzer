
# Network Analysis Tool

This tool is designed to help you analyze your network for performance issues, packet loss, and unauthorized devices using various tests such as speed tests, diagnostics, network scanning, stress testing, and packet loss testing. It is built using FastAPI, Speedtest, and iPerf3.

## Table of Contents
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Endpoints](#endpoints)
  - [Run Tests](#run-tests)
  - [Parameters](#parameters)
- [Running Locally](#running-locally)
- [Contributing](#contributing)
- [License](#license)

## Requirements

To run this script, you need to have the following installed on your system:
- **Python 3.7+**
- **FastAPI**: for creating the API.
- **iPerf3**: for running network stress tests and packet loss tests.
- **Nmap**: for scanning the network.
- **Psutil**: for gathering system and network information.
- **Speedtest-cli**: for running speed tests.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/network-analysis-tool.git
   cd network-analysis-tool
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install iPerf3**:
   - Download and install iPerf3 from [iPerf3 Website](https://iperf.fr/iperf-download.php).
   - Ensure that `iperf3` is added to your system's PATH.

5. **Install Nmap**:
   - Download and install Nmap from [Nmap Website](https://nmap.org/download.html).
   - Ensure Nmap is added to your system's PATH.

## Usage

To run the script, use the following command:

```bash
uvicorn main:app --reload
```

This will start the FastAPI server at `http://127.0.0.1:8000`.

## Endpoints

### Run Tests

You can run various network tests by making a `GET` request to:

```
http://127.0.0.1:8000/run_tests
```

### Parameters

| Parameter        | Type  | Default  | Description                                         |
|------------------|-------|----------|-----------------------------------------------------|
| `run_speed`      | bool  | true     | Run a network speed test using Speedtest.            |
| `run_diagnostics`| bool  | true     | Run network diagnostics (ping tests and interface info). |
| `run_scan`       | bool  | true     | Run a network scan to detect connected devices.      |
| `run_stress`     | bool  | true     | Run a network stress test using iPerf3.              |
| `run_packet_loss`| bool  | false    | Run a packet loss test using iPerf3 in UDP mode.     |

### Example Request

To run a packet loss test only:

```
GET http://127.0.0.1:8000/run_tests?run_speed=false&run_diagnostics=false&run_scan=false&run_stress=false&run_packet_loss=true
```

## Running Locally

1. **Start the FastAPI server**:
   ```bash
   uvicorn main:app --reload
   ```

2. **Access the API**:
   - Open your browser or use a tool like Postman to access `http://127.0.0.1:8000`.
   - Use the `/run_tests` endpoint to trigger the tests.

3. **View Results**:
   - The API will return the results of the tests as JSON.

## Contributing

If you'd like to contribute to the project, feel free to submit a pull request or open an issue.

1. Fork the repository.
2. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes and commit them:
   ```bash
   git commit -m "Add new feature"
   ```
4. Push to the branch:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Open a pull request.

## License

This project is licensed under the MIT License.

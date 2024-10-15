# Courier Application

## Overview

This is a web-based courier application that connects clients with drivers. It allows clients to post jobs, drivers to bid on these jobs, and facilitates the entire process from job creation to completion and driver rating.

## Features

- User authentication (login/signup) for clients and drivers
- Job posting by clients
- Bidding system for drivers to apply for jobs
- Job status tracking (open, in progress, completed by driver, paid, rated)
- Driver rating system
- Admin panel for user management

## Tech Stack

- Python
- Flask
- SQLAlchemy
- HTML/CSS
- Bootstrap

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/courier-application.git
   cd courier-application
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

1. Ensure you're in the project directory and your virtual environment is activated.

2. Run the Flask application:
   ```
   flask run
   ```

3. Open a web browser and navigate to `http://localhost:5000`

## Usage

1. Sign up as a client or driver
2. Clients can post jobs from their profile page
3. Drivers can view available jobs and place bids
4. Clients can accept bids, marking the job as in progress
5. Drivers mark jobs as completed when finished
6. Clients confirm payment and rate the driver's service

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.


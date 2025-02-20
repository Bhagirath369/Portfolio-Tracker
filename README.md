# TrackFolio

TrackFolio is an intuitive stock portfolio management platform that allows users to create an account, track their investments, and view live stock data fetched from Mero Lagani. The project was designed to simplify stock tracking and provide real-time financial insights.

## Team Members
- Bhagirath Padhya Aryal
- Devendra Panta
- Yuvraj Aryal
- Sudin Shrestha

## Project Overview
TrackFolio is built to help users manage their stock investments efficiently. The platform provides features such as user authentication, stock portfolio management, and real-time stock price updates. The technology stack includes:

- **Backend:** Django
- **Frontend:** HTML/CSS
- **Database:** PostgreSQL for storing user data and portfolio details
- **Stock Data Source:** Mero Lagani API for real-time stock updates

## Key Features

### User Management
TrackFolio provides a secure user authentication system, enabling users to:
- Register an account
- Log in securely
- Manage their profile

### Portfolio Management
Users can:
- Add different stocks to their portfolio
- Track investments over time
- View total investment value and individual stock performance

### Real-Time Stock Data
- Stock prices are fetched live from **Mero Lagani** to keep users updated.
- Users can view historical trends and price changes.

## Prerequisites
Before installing TrackFolio, ensure you have:
- **Python & Django** installed on your machine
- A **PostgreSQL** database set up
- A modern web browser

## Installation
Follow these steps to set up TrackFolio on your local machine:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/TrackFolio.git](https://github.com/Bhagirath369/Portfolio-Tracker
   ```

2. **Create a PostgreSQL database** and run the SQL scripts provided in `models/database.sql` to set up tables.

3. **Create an environment file:**
   - In the root directory, create a `.env` file.
   - Add the required environment variables as listed in `.env.example`.

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

## Usage
1. Open your web browser and go to `http://localhost:8000` (or the port set in `.env`).
2. Register a new account or log in with an existing one.
3. Add stocks to your portfolio and view real-time price updates.

## Issues Encountered
- **Stock Data Fetching:** Integrating Mero Lagani’s stock API required handling rate limits and ensuring data accuracy.
- **Portfolio Updates:** Managing live price updates dynamically without performance issues was a key challenge.
- **User Authentication:** Implementing a secure authentication flow with hashed passwords and session-based authentication.

## Contributing
We welcome contributions to TrackFolio! If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.

## License
TrackFolio is released under the MIT License. You are free to use, modify, and distribute the code under the license terms.

## Acknowledgments
- Thanks to open-source contributors and tools that made this project possible.
- Special thanks to **Mero Lagani** for providing real-time stock data.

## Future Enhancements
We plan to enhance TrackFolio with the following features:
- **Automated Alerts:** Notify users about significant stock price changes.
- **Graphical Analysis:** Interactive charts for better visualization of stock trends.
- **Mobile App:** Build a mobile version for better accessibility.
- **Dark Mode:** User-customizable themes for better UI/UX.

For more details, visit the project repositories:
- **[TrackFolio](https://github.com/Bhagirath369/Portfolio-Tracker/tree/main/TrackFolio)**

By continuously improving TrackFolio, we aim to provide an efficient and user-friendly stock tracking platform.


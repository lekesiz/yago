# Mobile App Test

## Project Description

The Mobile App Test project is a modern, full-stack mobile application designed to showcase the capabilities of a tech stack that includes JavaScript, React Native, Node.js with Express, and MongoDB. This project not only demonstrates the development of a cross-platform mobile application but also incorporates best practices in testing and DevOps. We use Jest for unit testing, Supertest for integration testing, and Detox for end-to-end testing. For DevOps, Docker is used for containerization, and GitHub Actions for continuous integration and continuous deployment (CI/CD).

## Features

- **Cross-Platform Mobile App**: Designed with React Native, the app offers a seamless experience on both iOS and Android devices.
- **Backend Services**: Utilizing Node.js with Express for efficient and scalable backend services.
- **Database Integration**: MongoDB is used for storing and retrieving data efficiently.
- **Comprehensive Testing**: Integrated testing suite with Jest, Supertest, and Detox for unit, integration, and end-to-end testing respectively.
- **DevOps Practices**: Incorporates Docker for containerization and GitHub Actions for CI/CD, ensuring smooth deployment and integration.

## Installation Instructions

### Prerequisites

- Node.js and npm (Node Package Manager)
- Docker
- MongoDB instance (local or remote)
- React Native environment setup (Refer to [React Native Environment Setup](https://reactnative.dev/docs/environment-setup))

### Steps

1. **Clone the Repository**

    ```sh
    git clone https://github.com/yourproject/mobile-app-test.git
    cd mobile-app-test
    ```

2. **Backend Setup**

    Navigate to the backend directory and install dependencies:

    ```sh
    cd backend
    npm install
    ```

    Start the backend server:

    ```sh
    npm start
    ```

3. **Frontend Setup**

    Open a new terminal window/tab, navigate to the frontend directory, and install dependencies:

    ```sh
    cd ../frontend
    npm install
    ```

    Run the React Native app:

    - For iOS:

        ```sh
        npx react-native run-ios
        ```

    - For Android:

        ```sh
        npx react-native run-android
        ```

4. **Running Tests**

    To run unit tests, integration tests, or end-to-end tests, navigate to the respective directories and use the npm test command:

    ```sh
    npm test
    ```

5. **Docker (Optional)**

    To containerize the application using Docker, ensure Docker is installed and running, then:

    ```sh
    docker-compose up --build
    ```

## Usage Examples

- **Fetching Data from Backend**

    Example of how to fetch data from the backend using React Native:

    ```javascript
    fetch('http://localhost:3000/api/data')
    .then((response) => response.json())
    .then((json) => console.log(json))
    .catch((error) => console.error(error));
    ```

## API Documentation

The backend API supports several endpoints for CRUD operations:

- **GET `/api/data`**: Fetches data from the database.
- **POST `/api/data`**: Adds new data to the database.
- **PUT `/api/data/:id`**: Updates existing data in the database.
- **DELETE `/api/data/:id`**: Deletes data from the database.

For more detailed API documentation, please refer to the `api-docs` directory in the backend.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
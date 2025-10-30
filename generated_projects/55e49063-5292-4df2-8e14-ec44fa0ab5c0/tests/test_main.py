// File: test/main.test.js

const request = require('supertest');
const mongoose = require('mongoose');
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const userRoutes = require('../src/routes/userRoutes');
const dashboardRoutes = require('../src/routes/dashboardRoutes');

// Setup an express app for testing
const app = express();
app.use(cors());
app.use(bodyParser.json());
app.use('/api/users', userRoutes);
app.use('/api/dashboard', dashboardRoutes);

// Error handling middleware for testing
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).send('Something broke!');
});

describe('Main Application Routes', () => {
    beforeAll(async () => {
        // Connect to a test database
        const dbUrl = 'mongodb://localhost:27017/mobileAppTestDB_Test';
        await mongoose.connect(dbUrl, { useNewUrlParser: true, useUnifiedTopology: true });
    });

    afterAll(async () => {
        // Disconnect from the test database
        await mongoose.connection.close();
    });

    describe('User Routes', () => {
        // Happy path test
        it('should create a new user', async () => {
            const userData = { name: 'John Doe', email: 'john@example.com' };
            const response = await request(app).post('/api/users').send(userData);
            expect(response.statusCode).toBe(201);
            expect(response.body).toHaveProperty('_id');
            expect(response.body.name).toBe(userData.name);
            expect(response.body.email).toBe(userData.email);
        });

        // Error handling test
        it('should not create a user with invalid data', async () => {
            const userData = { email: 'john@example.com' }; // Missing name
            const response = await request(app).post('/api/users').send(userData);
            expect(response.statusCode).toBe(400);
        });
    });

    describe('Dashboard Routes', () => {
        // Assuming dashboard routes require authentication, this is a simple example without it.
        // Happy path test
        it('should retrieve dashboard data', async () => {
            const response = await request(app).get('/api/dashboard');
            expect(response.statusCode).toBe(200);
            expect(response.body).toHaveProperty('data');
        });

        // Edge case test (assuming there's some form of access control or data filtering based on user)
        it('should not allow unauthorized access to dashboard', async () => {
            // This assumes there's middleware checking for auth which there isn't in the provided code.
            // This is illustrative of how you'd test for such a case.
            const response = await request(app).get('/api/dashboard');
            expect(response.statusCode).toBe(401);
        });
    });
});
// Import necessary libraries and dependencies
const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const jwt = require('jsonwebtoken');
const cors = require('cors');
const redis = require('redis');
const amqp = require('amqplib/callback_api');
const { Client } = require('@elastic/elasticsearch');
const userRoutes = require('./routes/userRoutes');
const testRoutes = require('./routes/testRoutes');
const searchRoutes = require('./routes/searchRoutes');
const analyticsRoutes = require('./routes/analyticsRoutes');
const notificationRoutes = require('./routes/notificationRoutes');
require('dotenv').config();

// Initialize express app
const app = express();

// MongoDB connection string
const mongoURI = process.env.MONGODB_URI;

// Connect to MongoDB
mongoose.connect(mongoURI, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log('MongoDB connected successfully'))
  .catch(err => console.error('MongoDB connection error:', err));

// Redis client setup
const redisClient = redis.createClient({
  url: process.env.REDIS_URL // Get Redis URL from environment variables
});
redisClient.on('error', (err) => console.log('Redis Client Error', err));
redisClient.connect();

// Elasticsearch client setup
const esClient = new Client({ node: process.env.ELASTICSEARCH_NODE });

// RabbitMQ connection setup
amqp.connect(process.env.RABBITMQ_URL, function(error0, connection) {
  if (error0) {
    throw error0;
  }
  console.log('RabbitMQ connected successfully');
  connection.on('error', (err) => console.log('RabbitMQ Connection Error', err));
});

// Middleware
app.use(cors());
app.use(bodyParser.json());

// JWT middleware to verify token
app.use((req, res, next) => {
  if (req.headers && req.headers.authorization) {
    jwt.verify(req.headers.authorization.split(' ')[1], process.env.JWT_SECRET, (err, decode) => {
      if (err) req.user = undefined;
      req.user = decode;
      next();
    });
  } else {
    req.user = undefined;
    next();
  }
});

// Routes
app.use('/api/users', userRoutes);
app.use('/api/tests', testRoutes);
app.use('/api/search', searchRoutes);
app.use('/api/analytics', analyticsRoutes);
app.use('/api/notifications', notificationRoutes);

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send('Something broke!');
});

// Server setup
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
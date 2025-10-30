// UserAPI - /api/users/register
app.post('/api/users/register', (req, res) => {
  const { username, password, email } = req.body;

  if (!username || !password || !email) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  // Check if user already exists
  if (users.find(user => user.username === username || user.email === email)) {
    return res.status(409).json({ error: 'User already exists' });
  }

  const newUser = { id: uuid(), username, password, email };
  users.push(newUser);

  res.status(201).json({ message: 'User registered successfully', user: newUser });
});

// UserAPI - /api/users/login
app.post('/api/users/login', (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  const user = users.find(user => user.username === username && user.password === password);

  if (!user) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  const token = jwt.sign({ userId: user.id }, 'secret_key');
  res.status(200).json({ message: 'Login successful', token });
});

// TestAPI - /api/tests
app.post('/api/tests', (req, res) => {
  const { name, description } = req.body;

  if (!name || !description) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  const newTest = { id: uuid(), name, description };
  tests.push(newTest);

  res.status(201).json({ message: 'Test created successfully', test: newTest });
});

// TestAPI - /api/tests/:id
app.get('/api/tests/:id', (req, res) => {
  const testId = req.params.id;
  const test = tests.find(test => test.id === testId);

  if (!test) {
    return res.status(404).json({ error: 'Test not found' });
  }

  res.status(200).json({ test });
});

// TestAPI - /api/tests
app.get('/api/tests', (req, res) => {
  res.status(200).json({ tests });
});
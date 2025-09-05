const express = require('express');
const path = require('path');
const landingRoutes = require('./routes/landing');

const app = express();

app.set('views', path.join(__dirname, '..', 'views'));
app.set('view engine', 'ejs');

// serve public static if exists
app.use(express.static(path.join(__dirname, '..', 'public')));

// mount landing routes at root
app.use('/', landingRoutes);

// fallback 404
app.use((req, res) => {
  res.status(404).send('Not Found');
});

const port = process.env.PORT || 3001;
app.listen(port, () => {
  console.log(`Server listening on http://localhost:${port}`);
});

module.exports = app;

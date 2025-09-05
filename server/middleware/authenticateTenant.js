// No-op tenant resolver for initial scaffolding
module.exports = function authenticateTenant(req, res, next) {
  req.tenant = req.tenant || { name: 'default' };
  return next();
};

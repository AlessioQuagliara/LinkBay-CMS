// Simple permissive requireRole stub
module.exports = function requireRole(_allowed) {
  return function (req, res, next) {
    return next();
  };
};

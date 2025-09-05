// Minimal auth controller scaffold (JS)
exports.home = function (req, res) {
  return res.render('landing/home', { title: 'LinkBay CMS' });
};

exports.register = async function (req, res) {
  // placeholder: implement real registration flow later
  return res.status(501).json({ ok: false, error: 'Registration not implemented' });
};

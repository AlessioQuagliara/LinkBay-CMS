"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const home = (req, res) => {
    res.render('landing/home', { title: 'LinkBay CMS' });
};
const register = async (req, res) => {
    // placeholder: implement tenant-aware registration here
    const { email } = req.body;
    return res.json({ ok: true, email });
};
exports.default = { home, register };

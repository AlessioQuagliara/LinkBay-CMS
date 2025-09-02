"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const jwtAuth_1 = require("../middleware/jwtAuth");
const router = (0, express_1.Router)();
// tenant dashboard pages require auth
router.get('/analytics', jwtAuth_1.jwtAuth, async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).send('tenant required');
    res.render('admin_analytics', { tenant });
});
exports.default = router;

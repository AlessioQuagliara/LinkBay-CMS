"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const pageController_1 = __importDefault(require("../controllers/pageController"));
const router = (0, express_1.Router)();
// catch-all for pages: marketing or tenant
router.get('*', pageController_1.default.renderPage);
exports.default = router;

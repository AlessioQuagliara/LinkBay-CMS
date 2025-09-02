"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.dynamicCors = void 0;
const cors_1 = __importDefault(require("cors"));
const whitelist = ['https://linkbay.example.com'];
const dynamicCors = (req, res, next) => {
    const origin = req.headers.origin;
    // tenant domains would be looked up from tenant config; allow if in whitelist for now
    if (!origin)
        return next();
    if (whitelist.includes(origin))
        return (0, cors_1.default)({ origin })(req, res, next);
    return next();
};
exports.dynamicCors = dynamicCors;

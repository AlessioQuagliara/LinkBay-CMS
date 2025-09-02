"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.hashPassword = hashPassword;
exports.comparePassword = comparePassword;
exports.signAccessToken = signAccessToken;
exports.signRefreshToken = signRefreshToken;
exports.verifyToken = verifyToken;
const jsonwebtoken_1 = __importDefault(require("jsonwebtoken"));
const bcryptjs_1 = __importDefault(require("bcryptjs"));
const dotenv_1 = __importDefault(require("dotenv"));
dotenv_1.default.config();
const JWT_SECRET = process.env.SESSION_SECRET || 'devsecret';
function hashPassword(password) {
    return bcryptjs_1.default.hash(password, 10);
}
function comparePassword(password, hash) {
    return bcryptjs_1.default.compare(password, hash);
}
function signAccessToken(payload, expiresIn = '15m') {
    const opts = { expiresIn };
    return jsonwebtoken_1.default.sign(payload, JWT_SECRET, opts);
}
function signRefreshToken(payload, expiresIn = '30d') {
    const opts = { expiresIn };
    return jsonwebtoken_1.default.sign(payload, JWT_SECRET, opts);
}
function verifyToken(token) {
    return jsonwebtoken_1.default.verify(token, JWT_SECRET);
}

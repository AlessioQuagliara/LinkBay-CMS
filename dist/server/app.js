"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const path_1 = __importDefault(require("path"));
const dotenv_1 = __importDefault(require("dotenv"));
const tenantResolver_1 = __importDefault(require("./middleware/tenantResolver"));
const authController_1 = __importDefault(require("./controllers/authController"));
const express_ejs_layouts_1 = __importDefault(require("express-ejs-layouts"));
const landing_1 = __importDefault(require("./routes/landing"));
dotenv_1.default.config();
const app = (0, express_1.default)();
const port = process.env.PORT || 3001;
app.set('views', path_1.default.join(__dirname, '..', 'views'));
app.set('view engine', 'ejs');
app.use(express_ejs_layouts_1.default);
// Do not set a global layout here; landing routes specify their own layout.
app.use(express_1.default.static(path_1.default.join(__dirname, '..', 'public')));
app.use(express_1.default.json());
app.use(express_1.default.urlencoded({ extended: true }));
// Attach tenant resolver early
app.use(tenantResolver_1.default);
// Routes
// Landing pages (use per-route layout)
app.use('/', landing_1.default);
// API / other controllers
app.post('/api/register', authController_1.default.register);
exports.default = app;
if (require.main === module) {
    app.listen(port, () => {
        // eslint-disable-next-line no-console
        console.log(`Server listening on http://localhost:${port}`);
    });
}

"use strict";
/**
 * LinkBay CMS Plugin SDK
 * This package exports the minimal, strict types and interfaces that a plugin
 * may implement to interact with the LinkBay core. The runtime will only
 * expose the approved surfaces from PluginContext, never raw Express/DB.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.CoreHook = exports.ExtensionPoint = void 0;
/** Allowed extension points - whitelist only these */
var ExtensionPoint;
(function (ExtensionPoint) {
    ExtensionPoint["HOOKS"] = "hooks";
    ExtensionPoint["API_ROUTES"] = "api_routes";
    ExtensionPoint["ADMIN_UI"] = "admin_ui";
    ExtensionPoint["EDITOR_BLOCKS"] = "editor_blocks";
})(ExtensionPoint || (exports.ExtensionPoint = ExtensionPoint = {}));
/** Hook types that core exposes. Plugins can register handlers for those hooks. */
var CoreHook;
(function (CoreHook) {
    CoreHook["PAGE_RENDER"] = "page.render";
    CoreHook["PRODUCT_SAVE"] = "product.save";
    CoreHook["ORDER_PLACED"] = "order.placed";
})(CoreHook || (exports.CoreHook = CoreHook = {}));
exports.default = {};

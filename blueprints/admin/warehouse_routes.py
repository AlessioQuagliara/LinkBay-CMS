from flask import Blueprint, request, render_template, redirect, url_for, flash
from models.database import db
from models.warehouse import Warehouse, Inventory, Location, InventoryMovement
from models.products import Product
from models.shoplist import ShopList
from helpers import check_user_authentication
from sqlalchemy.exc import SQLAlchemyError
import logging

warehouse_bp = Blueprint("warehouse", __name__)


# Dashboard WMS per Statistiche ------------------------------------------------------------------------------------------
@warehouse_bp.route("/admin/cms/warehouse/dashboard", methods=["GET"])
def warehouse_dashboard():
    username = check_user_authentication()
    if not username:
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_subdomain = request.host.split('.')[0]
    shop = db.session.query(ShopList).filter_by(shop_name=shop_subdomain).first()
    if not shop:
        flash('Nessun negozio trovato per questo nome.', 'warning')
        return redirect(url_for('ui.homepage'))

    try:
        warehouses = Warehouse.query.filter_by(shop_id=shop.id).all()
        total_warehouses = len(warehouses)

        total_locations = Location.query.join(Warehouse).filter(Warehouse.shop_id == shop.id).count()

        total_movements = InventoryMovement.query.filter_by(shop_id=shop.id).count()

        total_quantity = db.session.query(db.func.sum(Inventory.quantity))\
            .filter(Inventory.shop_id == shop.id).scalar() or 0

    except SQLAlchemyError as e:
        logging.error(f"Errore nel recupero dati dashboard magazzino: {str(e)}")
        flash("Errore nel caricamento della dashboard di magazzino", "danger")
        return redirect(url_for('ui.homepage'))

    return render_template(
        "admin/cms/warehouse/dashboard.html",
        title="Dashboard Magazzino",
        username=username,
        shop=shop,
        total_warehouses=total_warehouses,
        total_locations=total_locations,
        total_movements=total_movements,
        total_quantity=total_quantity
    )


# Lista dei Magazzini ------------------------------------------------------------------------------------------
@warehouse_bp.route("/admin/cms/warehouse/list_warehouses", methods=["GET"])
def list_warehouses():
    username = check_user_authentication()
    if not username:
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_subdomain = request.host.split('.')[0]
    shop = db.session.query(ShopList).filter_by(shop_name=shop_subdomain).first()
    if not shop:
        flash('Nessun negozio trovato per questo nome.', 'warning')
        return redirect(url_for('ui.homepage'))

    warehouses = Warehouse.query.filter_by(shop_id=shop.id).all()
    return render_template("admin/cms/warehouse/warehouses.html", username=username, shop=shop, warehouses=warehouses)


# Crea un nuovo Magazzino ------------------------------------------------------------------------------------------
@warehouse_bp.route("/admin/cms/warehouse/create", methods=["GET", "POST"])
def create_warehouse_view():
    username = check_user_authentication()
    if not username:
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_subdomain = request.host.split('.')[0]
    shop = db.session.query(ShopList).filter_by(shop_name=shop_subdomain).first()
    if not shop:
        flash('Nessun negozio trovato per questo nome.', 'warning')
        return redirect(url_for('ui.homepage'))

    if request.method == "POST":
        name = request.form.get("name")
        address = request.form.get("address")
        if not name:
            flash("Il nome del magazzino è obbligatorio.", "danger")
            return redirect(request.url)
        warehouse = Warehouse(shop_id=shop.id, name=name, address=address)
        db.session.add(warehouse)
        db.session.commit()
        flash("Magazzino creato con successo!", "success")
        return redirect(url_for("warehouse.list_warehouses"))

    return render_template("admin/cms/warehouse/warehouse_create.html", username=username, shop=shop)


# Modifica un Magazzino ------------------------------------------------------------------------------------------
@warehouse_bp.route("/admin/cms/warehouse/edit/<int:warehouse_id>", methods=["GET", "POST"])
def edit_warehouse_view(warehouse_id):
    username = check_user_authentication()
    if not username:
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    warehouse = Warehouse.query.get_or_404(warehouse_id)

    if request.method == "POST":
        warehouse.name = request.form.get("name")
        warehouse.address = request.form.get("address")
        db.session.commit()
        flash("Magazzino aggiornato con successo!", "success")
        return redirect(url_for("warehouse.list_warehouses"))

    return render_template("admin/cms/warehouse/warehouse_edit.html", username=username, warehouse=warehouse)


# Elimina un Magazzino ------------------------------------------------------------------------------------------
@warehouse_bp.route("/admin/cms/warehouse/delete/<int:warehouse_id>", methods=["POST"])
def delete_warehouse_view(warehouse_id):
    username = check_user_authentication()
    if not username:
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    warehouse = Warehouse.query.get_or_404(warehouse_id)
    db.session.delete(warehouse)
    db.session.commit()
    flash("Magazzino eliminato con successo!", "success")
    return redirect(url_for("warehouse.list_warehouses"))



# Lista delle Ubicazioni ------------------------------------------------------------------------------------------
@warehouse_bp.route("/admin/cms/warehouse/list_locations", methods=["GET"])
def list_locations():
    username = check_user_authentication()
    if not username:
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_subdomain = request.host.split('.')[0]
    shop = db.session.query(ShopList).filter_by(shop_name=shop_subdomain).first()
    if not shop:
        flash('Nessun negozio trovato per questo nome.', 'warning')
        return redirect(url_for('ui.homepage'))

    locations = Location.query.join(Warehouse).filter(Warehouse.shop_id == shop.id).all()
    return render_template("admin/cms/warehouse/locations.html", username=username, shop=shop, locations=locations)


# Crea una nuova Ubicazione ------------------------------------------------------------------------------------------
@warehouse_bp.route("/admin/cms/warehouse/location/create", methods=["GET", "POST"])
def create_location_view():
    username = check_user_authentication()
    if not username:
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    warehouses = Warehouse.query.all()
    if request.method == "POST":
        warehouse_id = request.form.get("warehouse_id")
        code = request.form.get("code")
        description = request.form.get("description")
        if not warehouse_id or not code:
            flash("ID magazzino e codice sono obbligatori.", "danger")
            return redirect(request.url)
        location = Location(warehouse_id=warehouse_id, code=code, description=description)
        db.session.add(location)
        db.session.commit()
        flash("Ubicazione creata con successo!", "success")
        return redirect(url_for("warehouse.list_locations"))

    return render_template("admin/cms/warehouse/location_create.html", username=username, warehouses=warehouses)


# Modifica un'Ubicazione ------------------------------------------------------------------------------------------
@warehouse_bp.route("/admin/cms/warehouse/location/edit/<int:location_id>", methods=["GET", "POST"])
def edit_location_view(location_id):
    username = check_user_authentication()
    if not username:
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    location = Location.query.get_or_404(location_id)
    warehouses = Warehouse.query.all()

    if request.method == "POST":
        location.warehouse_id = request.form.get("warehouse_id")
        location.code = request.form.get("code")
        location.description = request.form.get("description")
        db.session.commit()
        flash("Ubicazione aggiornata con successo!", "success")
        return redirect(url_for("warehouse.list_locations"))

    return render_template("admin/cms/warehouse/location_edit.html", username=username, location=location, warehouses=warehouses)


# Elimina un'Ubicazione ------------------------------------------------------------------------------------------
@warehouse_bp.route("/admin/cms/warehouse/location/delete/<int:location_id>", methods=["POST"])
def delete_location_view(location_id):
    username = check_user_authentication()
    if not username:
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    location = Location.query.get_or_404(location_id)
    db.session.delete(location)
    db.session.commit()
    flash("Ubicazione eliminata con successo!", "success")
    return redirect(url_for("warehouse.list_locations"))


# Lista delle Giacenze (Inventory) ------------------------------------------------------------------------------------------
@warehouse_bp.route("/admin/cms/warehouse/list_inventory", methods=["GET"])
def list_inventory():
    username = check_user_authentication()
    if not username:
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_subdomain = request.host.split('.')[0]
    shop = db.session.query(ShopList).filter_by(shop_name=shop_subdomain).first()
    if not shop:
        flash('Nessun negozio trovato per questo nome.', 'warning')
        return redirect(url_for('ui.homepage'))

    inventory = Inventory.query.filter_by(shop_id=shop.id).all()
    # Mapping IDs to names for display
    warehouse_map = {w.id: w.name for w in Warehouse.query.filter_by(shop_id=shop.id).all()}
    location_map = {l.id: l.code for l in Location.query.join(Warehouse).filter(Warehouse.shop_id == shop.id).all()}
    product_map = {p.id: p.name for p in Product.query.filter_by(shop_id=shop.id).all()}
    return render_template(
        "admin/cms/warehouse/inventory.html",
        username=username,
        shop=shop,
        inventory=inventory,
        warehouse_map=warehouse_map,
        location_map=location_map,
        product_map=product_map
    )


# Crea una nuova Giacenza ------------------------------------------------------------------------------------------
@warehouse_bp.route("/admin/cms/warehouse/inventory/create", methods=["GET", "POST"])
def create_inventory():
    username = check_user_authentication()
    if not username:
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for("user.login"))

    shop_subdomain = request.host.split('.')[0]
    shop = db.session.query(ShopList).filter_by(shop_name=shop_subdomain).first()
    if not shop:
        flash("Nessun negozio trovato per questo nome.", "warning")
        return redirect(url_for("ui.homepage"))

    products = Product.query.filter_by(shop_id=shop.id).all()
    warehouses = Warehouse.query.filter_by(shop_id=shop.id).all()
    locations = Location.query.join(Warehouse).filter(Warehouse.shop_id == shop.id).all()

    if request.method == "POST":
        product_id = request.form.get("product_id")
        warehouse_id = request.form.get("warehouse_id")
        location_id = request.form.get("location_id") or None
        quantity = int(request.form.get("quantity") or 0)
        reserved = int(request.form.get("reserved") or 0)

        inventory = Inventory(
            shop_id=shop.id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            location_id=location_id,
            quantity=quantity,
            reserved=reserved
        )
        db.session.add(inventory)
        db.session.commit()
        flash("Giacenza creata con successo!", "success")
        return redirect(url_for("warehouse.list_inventory"))

    return render_template("admin/cms/warehouse/inventory_create.html", username=username, shop=shop, products=products, warehouses=warehouses, locations=locations)


# Modifica una Giacenza ------------------------------------------------------------------------------------------
@warehouse_bp.route("/admin/cms/warehouse/inventory/edit/<int:inventory_id>", methods=["GET", "POST"])
def edit_inventory(inventory_id):
    username = check_user_authentication()
    if not username:
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for("user.login"))

    shop_subdomain = request.host.split('.')[0]
    shop = db.session.query(ShopList).filter_by(shop_name=shop_subdomain).first()
    if not shop:
        flash("Nessun negozio trovato per questo nome.", "warning")
        return redirect(url_for("ui.homepage"))

    inventory = Inventory.query.get_or_404(inventory_id)

    products = Product.query.filter_by(shop_id=shop.id).all()
    warehouses = Warehouse.query.filter_by(shop_id=shop.id).all()
    locations = Location.query.join(Warehouse).filter(Warehouse.shop_id == shop.id).all()

    if request.method == "POST":
        inventory.product_id = request.form.get("product_id")
        inventory.warehouse_id = request.form.get("warehouse_id")
        inventory.location_id = request.form.get("location_id") or None
        inventory.quantity = int(request.form.get("quantity") or 0)
        inventory.reserved = int(request.form.get("reserved") or 0)

        db.session.commit()
        flash("Giacenza aggiornata con successo!", "success")
        return redirect(url_for("warehouse.list_inventory"))

    return render_template(
        "admin/cms/warehouse/inventory_edit.html",
        username=username,
        inventory=inventory,
        shop=shop,
        products=products,
        warehouses=warehouses,
        locations=locations
    )


# Elimina una Giacenza ------------------------------------------------------------------------------------------
@warehouse_bp.route("/admin/cms/warehouse/inventory/delete/<int:inventory_id>", methods=["POST"])
def delete_inventory(inventory_id):
    username = check_user_authentication()
    if not username:
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for("user.login"))

    inventory = Inventory.query.get_or_404(inventory_id)
    db.session.delete(inventory)
    db.session.commit()
    flash("Giacenza eliminata con successo!", "success")
    return redirect(url_for("warehouse.list_inventory"))


# Lista dei Movimenti di Magazzino ------------------------------------------------------------------------------------------
@warehouse_bp.route("/admin/cms/warehouse/list_inventory_movements", methods=["GET"])
def list_inventory_movements():
    username = check_user_authentication()
    if not username:
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_subdomain = request.host.split('.')[0]
    shop = db.session.query(ShopList).filter_by(shop_name=shop_subdomain).first()
    if not shop:
        flash('Nessun negozio trovato per questo nome.', 'warning')
        return redirect(url_for('ui.homepage'))

    movements = InventoryMovement.query.filter_by(shop_id=shop.id).order_by(InventoryMovement.created_at.desc()).all()
    return render_template("admin/cms/warehouse/movements.html", username=username, shop=shop, movements=movements)

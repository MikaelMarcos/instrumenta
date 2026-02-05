from app import app, db, Equipment

with app.app_context():
    if not Equipment.query.filter_by(brand='Euromag').first():
        new_eq = Equipment(
            brand='Euromag', 
            model='Carretel', 
            type='Eletromagnético', 
            power_supply='N/A',
            password_user='', 
            password_admin='', 
            menu_shortcuts='', 
            notes='Senha: 231042'
        )
        db.session.add(new_eq)
        db.session.commit()
        print("Euromag added successfully!")
    else:
        print("Euromag already exists.")

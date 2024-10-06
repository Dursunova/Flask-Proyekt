from flask import render_template, redirect, url_for, request, flash, session, abort
from app import app
from models import *
from flask_login import login_required, current_user, LoginManager
from forms import *
from werkzeug.security import generate_password_hash



from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf import CSRFProtect



from flask_wtf.csrf import CSRFProtect



# from flask_mail import Mail, Message

# app.config['MAIL_SERVER'] = 'smtp.example.com'  # Mail serverinizi buraya əlavə edin
# app.config['MAIL_PORT'] = 587  # Və ya SSL üçün 465
# app.config['MAIL_USERNAME'] = 'your-email@example.com'
# app.config['MAIL_PASSWORD'] = 'your-email-password'
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = False

# mail = Mail(app)


app.config['SECRET_KEY'] = 'my-secret-pw'  
csrf = CSRFProtect(app)


login_manager = LoginManager()
login_manager.init_app(app)

# User loader funksiyası
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# # Set locale for currency formatting
# locale.setlocale(locale.LC_ALL, '') 


# import pymysql
# from flask_mysqldb import MySQL

# mysql = MySQL(app)






@app.route('/')
def index():
    products = Product.query.all()
    categories = Category.query.all()

    cat_ids =  request.args.get('cat')
    if cat_ids:
        products = []
        cat_ids = cat_ids.split(',')

        for i in categories:
            categories = Category.query.filter_by(parent_id=i.id).all()
            product = Product.query.filter_by(category_id=i.id).all()
            products.extend(product)
            i.count = len(product)
            if i.children:
                for j in i.children:
                    product = Product.query.filter_by(category_id=j.id).all()
                    products.extend(product)
                i.count = len(products)
        

    context = {
        'products': products,
        'categories': categories
    }
    return render_template('shop.html', **context)




@app.route('/product')
def shop():
    category_id = request.args.get('category_id', type=int)
    search_query = request.args.get('name', type=str)  

    categories = Category.query.all()

    if search_query:
        products = Product.query.filter(Product.name.ilike(f'%{search_query}%')).all()
    elif category_id:
        products = Product.query.filter_by(category_id=category_id).all()
    else:
        products = Product.query.all()


    return render_template('shop.html', products=products, categories=categories)



# @app.route('/detail/<int:product_id>')
# def detail(product_id):
#    product = Product.query.get_or_404(product_id)  # Spesifik məhsulu ID-ə görə əldə edin
#    reviews = Review.query.filter_by(product_id=product_id).all() 
    
#    return render_template('detail.html', product=product, reviews=reviews)


#REVIEWWWWWWWWWWWWWWWWWWWWWW

@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    reviews = Review.query.filter_by(product_id=product_id).all()
    similar_products = Product.query.filter(Product.category_id == product.category_id, Product.id != product_id).limit(4).all()
    form = ReviewForm()
    
    # Form handling
    if form.validate_on_submit():
        if current_user.is_authenticated:
            new_review = Review(
                user_id=current_user.id,
                product_id=product.id,
                content=form.content.data,
                rating=form.rating.data
            )
            db.session.add(new_review)
            db.session.commit()
            flash('Your review has been submitted!', 'success')
            return redirect(url_for('product_detail', product_id=product_id))
        else:
            flash('You must be logged in to submit a review.', 'warning')
            return redirect(url_for('login'))

    return render_template('detail.html', product=product, reviews=reviews, similar_products=similar_products, form=form)






# @app.route('/add_review/<int:product_id>', methods=['POST'])
# @login_required
# def add_review(product_id):
#     product = Product.query.get_or_404(product_id)
#     review_content = request.form.get('review_content')
    
#     if not review_content:
#         flash("Rəy boş ola bilməz", "warning")
#         return redirect(url_for('product_detail', product_id=product_id))
    
#     # Yeni rəy yaradın
#     new_review = Review(content=review_content, user_id=current_user.id, product_id=product.id)
    
#     db.session.add(new_review)
#     db.session.commit()
    
#     flash("Rəyiniz əlavə olundu!", "success")
#     return redirect(url_for('product_detail', product_id=product.id))


#FAVORITESSSSSSSSSSS

@app.route('/favorites')
@login_required
def favorites():
    user_favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    favorites_count = Favorite.query.filter_by(user_id=current_user.id).count()
    return render_template('favorites.html',favorites_count=favorites_count, favorites=user_favorites)

@app.route('/add_to_favorites/<int:product_id>', methods=['POST'])
@login_required
def add_to_favorites(product_id):
    product = Product.query.get_or_404(product_id)
    existing_favorite = Favorite.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if not existing_favorite:
        new_favorite = Favorite(user_id=current_user.id, product_id=product_id)
        db.session.add(new_favorite)
        db.session.commit()
        flash('Product added to your favorites!', 'success')
    else:
        flash('Product is already in your favorites!', 'info')

    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/remove_from_favorites/<int:product_id>', methods=['POST'])
@login_required
def remove_from_favorites(product_id):
    favorite = Favorite.query.filter_by(user_id=current_user.id, product_id=product_id).first_or_404()
    db.session.delete(favorite)
    db.session.commit()
    flash('Product removed from your favorites!', 'success')
    return redirect(url_for('favorites'))




#LOGINNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):  # Şifrəni yoxlayırıq
            login_user(user)
            flash('Sistemə daxil oldunuz!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login uğursuz oldu. Email və ya şifrə yanlışdır.', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# def is_password_complex(password):
#     import re
#     # Check for at least one digit
#     if not re.search(r'\d', password):
#         return False
#     # Check for at least one lowercase letter
#     if not re.search(r'[a-z]', password):
#         return False
#     # Check for at least one uppercase letter
#     if not re.search(r'[A-Z]', password):
#         return False
#     # Check for at least one special character (@, #, or $)
#     if not re.search(r'[@#$]', password):
#         return False
#     return True


#REGISTERRRRRRRRRRRRRRRRR

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        
      
        new_user = User(name=form.name.data, email=form.email.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)
    




# CONTACTTTTTTTTTT


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        subject = form.subject.data
        message = form.message.data

        new_contact = Contact(name=name, email=email, subject=subject, message=message)
        db.session.add(new_contact)
        db.session.commit()

        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html',form=form)





# ADMINNNNNNN PANELLL

@app.route('/admin/products')
def admin_products():
    products = Product.query.all()
    
    return render_template('admin_product.html', products=products)



@app.route('/admin/product/create', methods=['GET', 'POST'])
def create_product():
    form = ProductForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]

    if form.validate_on_submit():
        name = form.name.data
        price = form.price.data
        discounted_price = form.discount_price.data or None  
        image_url = form.image_url.data or ''
        
        if not image_url:
            flash("Image URL is required", "danger")
            return render_template('admin_pro_form.html', form=form)
     
        new_product = Product(
            name=name,
            price=price,
            discounted_price=discounted_price,
            image=image_url,
            category_id=form.category.data 
        )
      
        db.session.add(new_product)
        db.session.commit()
        
        flash('Product created successfully!', 'success')
        return redirect(url_for('admin_products'))  
    
    return render_template('admin_pro_form.html', form=form)


@app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
    if form.validate_on_submit():
        product.name = form.name.data
        product.price = form.price.data
        product.category_id = form.category.data
        product.image= form.image_url.data
        product.discounted_price = form.discount_price.data

        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin_products'))
    return render_template('admin_pro_form.html', form=form, product=product)

@app.route('/admin/product/delete/<int:product_id>')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin_products'))



@app.route('/admin/products')
@login_required
def admin_productss():
    if not current_user.is_admin:
        abort(403)  # Forbidden
    products = Product.query.all()
    return render_template('admin_product.html', products=products)




# DISCOUNTEDDD

@app.route('/discounted')
def discounted_products():
    products = Product.query.filter(Product.discounted_price > 0).all()
    return render_template('discounted.html', products=products)

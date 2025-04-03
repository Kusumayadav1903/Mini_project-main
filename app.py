from flask import Flask, render_template, request, redirect, jsonify
from flask import Flask, render_template, request, redirect, url_for


from utils.db import db

from models.country import *




app =  Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///country.db'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/country')
def country():
    return render_template('country.html')

@app.route('/country_specific_data')
def country_specific_data():
    country = (Country.query.all())
    return render_template('country_specific_data.html', content=country)


@app.route('/dashboard', methods=['GET'])
def dashboard():
    countries = Country.query.all()  # Fetch all country data from the database
    country_data = [{
        'country_id': country.country_id,
        'country_name': country.country_name,
        'literacy_rate': country.literacy_rate,
        'enrollment_rate': country.enrollment_rate,
        'primary_education': country.primary_education,
        'secondary_education': country.secondary_education
    } for country in countries]

    return render_template('dashboard.html', content=country_data)



@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Capture form data
        name = request.form.get('name')
        contact = request.form.get('contact')
        support = request.form.get('support')

        # You can process the form data here if needed, like saving it to a database or sending an email.

        # For now, just redirect to the thank_you page
        return redirect(url_for('thank_you'))

    return render_template('contact.html')



@app.route('/thank-you')
def thank_you():
    print("Thank You page rendered.")
    return render_template('thank_you.html')



@app.route('/submit_contact_form', methods=['POST'])
def submit_contact_form():
    name = request.form.get('name')
    contact = request.form.get('contact')
    support = request.form.get('support')
    return redirect('/thank_you')



db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/submit', methods=['POST'])
def submit():
    form_data = request.form.to_dict()
    print(f"form_data: {form_data}")

    country_id = form_data.get('country_id')
    country_name = form_data.get('country_name')
    literacy_rate = form_data.get('literacy_rate')
    enrollment_rate = form_data.get('enrollment_rate')
    primary_education = form_data.get('primary_education')
    secondary_education = form_data.get('secondary_education')

    country = Country.query.filter_by(country_id=country_id).first()
    if not country:
        country = Country(country_id=country_id, country_name=country_name, literacy_rate=literacy_rate, enrollment_rate=enrollment_rate, primary_education=primary_education,secondary_education=secondary_education)
        db.session.add(country)
        db.session.commit()
    print("sumitted successfully")
    return redirect('/')



@app.route('/delete/<int:country_id>', methods=['GET', 'DELETE'])
def delete(country_id):
    country = Country.query.get(country_id)
    print("task: {}".format(country_id))

    if not country:
        return jsonify({'message': 'country not found'}), 404
    try:
        db.session.delete(country)
        db.session.commit()
        return jsonify({'message': 'country deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred while deleting the data {}'.format(e)}), 500


@app.route('/update/<int:country_id>', methods=['GET', 'POST'])
def update(country_id):
    country = Country.query.get_or_404(country_id)
    print(country.country_id)
    if not country:
        return jsonify({'message': 'country not found'}), 404

    if request.method == 'POST':
        country.country_id = request.form['country_id']
        country.country_name = request.form['country_name']
        country.literacy_rate = request.form['literacy_rate']
        country.enrollment_rate = request.form['enrollment_rate']
        country.primary_education = request.form['primary_education']
        country.secondary_education = request.form['secondary_education']

        try:
            db.session.commit()
            return redirect('/country_specific_data')

        except Exception as e:
            db.session.rollback()
            return "there is an issue while updating the record"
    return render_template('update.html', country=country)



@app.route('/trends', methods=['GET'])
def trends():
    order = request.args.get('order', 'asc')  # Default to ascending order
    if order == 'desc':
        countries_data = Country.query.order_by(Country.literacy_rate.desc()).all()
    else:
        countries_data = Country.query.order_by(Country.literacy_rate.asc()).all()

    # Prepare data for the chart
    chart_data = {
        "countries": [country.country_name for country in countries_data],
        "literacy_rates": [country.literacy_rate for country in countries_data],
    }

    return render_template('trends.html',
                           content=countries_data,  # Renamed variable to avoid shadowing
                           chart_data=chart_data,
                           order=order)



if __name__ =='__main__':
    app.run(host='127.0.0.1',port=5003,debug=True)
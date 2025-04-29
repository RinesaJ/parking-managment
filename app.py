from flask import Flask, render_template, request, redirect, url_for
import time

app = Flask(__name__)

# Initialize data
parking_data = {
    'Vehicle_Number': ['XXXX-XX-XXXX'],
    'Vehicle_Type': ['Bike'],
    'vehicle_Name': ['Intruder'],
    'Owner_Name': ['Unknown'],
    'Date': ['22-22-3636'],
    'Time': ['22:22:22'],
    'counts': {
        'bikes': 100,
        'cars': 250,
        'bicycles': 78
    }
}

@app.route('/')
def index():
    return render_template('index.html', parking_data=parking_data)

@app.route('/entry', methods=['GET', 'POST'])
def vehicle_entry():
    if request.method == 'POST':
        vno = request.form.get('vno', '').upper()
        vtype = request.form.get('vtype', '').lower()
        vname = request.form.get('vname', '')
        oname = request.form.get('oname', '')
        date = request.form.get('date', '')
        entry_time = request.form.get('time', '')

        if not vno or len(vno) != 12:
            return render_template('entry.html', error="Invalid vehicle number")
        
        if vno in parking_data['Vehicle_Number']:
            return render_template('entry.html', error="Vehicle already exists")
        
        if vtype not in ['a', 'b', 'c']:
            return render_template('entry.html', error="Invalid vehicle type")
        
        if not all([vname, oname, date, entry_time]):
            return render_template('entry.html', error="All fields are required")

        parking_data['Vehicle_Number'].append(vno)
        parking_data['vehicle_Name'].append(vname)
        parking_data['Owner_Name'].append(oname)
        parking_data['Date'].append(date)
        parking_data['Time'].append(entry_time)
        
        if vtype == 'a':
            parking_data['Vehicle_Type'].append('Bicycle')
            parking_data['counts']['bicycles'] -= 1
        elif vtype == 'b':
            parking_data['Vehicle_Type'].append('Bike')
            parking_data['counts']['bikes'] -= 1
        elif vtype == 'c':
            parking_data['Vehicle_Type'].append('Car')
            parking_data['counts']['cars'] -= 1

        return redirect(url_for('view_parked'))
    
    return render_template('entry.html')

@app.route('/remove', methods=['GET', 'POST'])
def remove_vehicle():
    if request.method == 'POST':
        vno = request.form.get('vno', '').upper()
        
        if not vno or len(vno) != 12:
            return render_template('remove.html', error="Invalid vehicle number")
        
        if vno not in parking_data['Vehicle_Number']:
            return render_template('remove.html', error="Vehicle not found")
        
        index = parking_data['Vehicle_Number'].index(vno)
        
        vtype = parking_data['Vehicle_Type'][index]
        if vtype == 'Bicycle':
            parking_data['counts']['bicycles'] += 1
        elif vtype == 'Bike':
            parking_data['counts']['bikes'] += 1
        elif vtype == 'Car':
            parking_data['counts']['cars'] += 1
        
        for key in ['Vehicle_Number', 'Vehicle_Type', 'vehicle_Name', 'Owner_Name', 'Date', 'Time']:
            parking_data[key].pop(index)
        
        return redirect(url_for('view_parked'))
    
    return render_template('remove.html')

@app.route('/view')
def view_parked():
    vehicles = zip(
        parking_data['Vehicle_Number'],
        parking_data['Vehicle_Type'],
        parking_data['vehicle_Name'],
        parking_data['Owner_Name'],
        parking_data['Date'],
        parking_data['Time']
    )
    return render_template('view.html', vehicles=vehicles, count=len(parking_data['Vehicle_Number']) - 1)

@app.route('/spaces')
def view_spaces():
    return render_template('spaces.html', counts=parking_data['counts'])

@app.route('/rates')
def view_rates():
    return render_template('rates.html')

@app.route('/bill', methods=['GET', 'POST'])
def generate_bill():
    if request.method == 'POST':
        vno = request.form.get('vno', '').upper()
        duration = request.form.get('duration', '0')  # Duration in minutes
        
        if not vno or len(vno) != 12:
            return render_template('bill.html', error="Invalid vehicle number")
        
        if vno not in parking_data['Vehicle_Number']:
            return render_template('bill.html', error="Vehicle not found")
        
        try:
            duration_minutes = int(duration)
            if duration_minutes < 0:
                raise ValueError
        except ValueError:
            return render_template('bill.html', error="Invalid duration")
        
        # Convert minutes to hours (round up to the nearest hour)
        fractional_hours = (duration_minutes + 59) // 60  # Round up to the nearest hour

        # Calculate parking charge based on the given rates
        if fractional_hours == 1:
            charge = 1  # 1 Euro for the first hour
        elif 2 <= fractional_hours <= 5:
            charge = 5  # 5 Euros for 2 to 5 hours
        else:
            charge = 10  # 10 Euros for more than 5 hours

        index = parking_data['Vehicle_Number'].index(vno)
        vtype = parking_data['Vehicle_Type'][index]

        return render_template('bill.html', 
                            vno=vno,
                            checkin_time=parking_data['Time'][index],
                            checkin_date=parking_data['Date'][index],
                            vtype=vtype,
                            duration_minutes=duration_minutes,
                            charge=charge,
                            show_result=True)
    
    # Show empty form if no POST request
    return render_template('bill.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
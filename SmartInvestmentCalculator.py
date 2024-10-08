import math
import streamlit as st



def calculate_financial(output_variable, **inputs):
    result = None
    if output_variable == 'corpus':
        principal = inputs['initial_investment']
        rate = inputs['rate_of_return'] / 100
        time = inputs['years']
        sip = inputs['sip_amount']
        step_up = inputs['stepup_percentage'] / 100
        
        monthly_rate = rate / 12
        months = int(time * 12)
        
        corpus = principal * (1 + monthly_rate) ** months  # Future value of initial investment
        
        future_value_factor = ((1 + monthly_rate) ** months - 1) / monthly_rate
        corpus += sip * future_value_factor * (1 + monthly_rate)  # Future value of SIP payments
        
        result = corpus

    elif output_variable == 'initial_investment':
        corpus = inputs['corpus']
        rate = inputs['rate_of_return'] / 100
        time = inputs['years']
        sip = inputs['sip_amount']
        step_up = inputs['stepup_percentage'] / 100
        
        monthly_rate = rate / 12
        months = int(time * 12)
        
        total_sip = 0
        monthly_sip = sip
        for month in range(months):
            total_sip *= (1 + monthly_rate)
            total_sip += monthly_sip
            if (month + 1) % 12 == 0:  # Apply step-up annually
                monthly_sip *= (1 + step_up)
        
        result = (corpus - total_sip) / (1 + rate) ** time

    elif output_variable == 'rate_of_return':
        principal = inputs['initial_investment']
        corpus = inputs['corpus']
        time = inputs['years']
        sip = inputs['sip_amount']
        step_up = inputs['stepup_percentage'] / 100
        
        months = int(time * 12)
        
        # Set up binary search for the rate of return
        low = 0  # Starting from 0% return
        high = 1  # Upper bound of 100% return
        epsilon = 1e-6  # Precision for binary search
        
        while high - low > epsilon:
            rate = (low + high) / 2
            monthly_rate = rate / 12
            
            # Calculate future value of SIPs
            future_value_factor = ((1 + monthly_rate) ** months - 1) / monthly_rate
            future_value_sip = sip * future_value_factor * (1 + monthly_rate)
            
            # Calculate future value of the principal
            future_value_principal = principal * (1 + monthly_rate) ** months
            estimated_corpus = future_value_sip + future_value_principal
            
            # Compare the estimated corpus with the target corpus
            if estimated_corpus < corpus:
                low = rate  # Increase the rate
            else:
                high = rate  # Decrease the rate
        
        result = (low + high) / 2 * 100  # Convert to annual percentage
    
    elif output_variable == 'years':
        principal = inputs['initial_investment']
        corpus = inputs['corpus']
        rate = inputs['rate_of_return'] / 100
        sip = inputs['sip_amount']
        step_up = inputs['stepup_percentage'] / 100
        
        monthly_rate = rate / 12
        months = 0
        current_corpus = principal
        monthly_sip = sip
        
        while current_corpus < corpus:
            current_corpus *= (1 + monthly_rate)
            current_corpus += monthly_sip
            months += 1
            if months % 12 == 0:
                monthly_sip *= (1 + step_up)
        
        result = months / 12

    elif output_variable == 'sip_amount':
        corpus = inputs.get('corpus', 0)
        principal = inputs.get('initial_investment', 0)
        rate = inputs.get('rate_of_return', 0) / 100
        time = inputs.get('years', 0)
        step_up = inputs.get('stepup_percentage', 0) / 100
        
        # Monthly rate of return
        monthly_rate = rate / 12
        months = int(time * 12)

        sip = corpus / (months * 12)  # A reasonable starting point
        max_iterations = 1000  # Maximum iterations to avoid infinite loop
        iteration = 0
        tolerance = 0.01
        
        def calculate_corpus(sip_guess):
            """Calculate corpus based on the current SIP guess and step-up."""
            total_corpus = principal
            yearly_sip = sip_guess * 12  # Convert monthly SIP to yearly
            for year in range(int(time)):
                for month in range(12):
                    total_corpus *= (1 + monthly_rate)
                    total_corpus += yearly_sip / 12
                yearly_sip *= (1 + step_up)
            return total_corpus
        
        # Iterative approach to adjust SIP and converge towards expected corpus
        while iteration < max_iterations:
            calculated_corpus = calculate_corpus(sip)
            error = corpus - calculated_corpus
            
            if abs(error) < tolerance:
                break
            
            # Adjust SIP value
            adjustment_factor = error / corpus
            sip += sip * adjustment_factor * 0.5  # Dampening factor to avoid overshooting
            
            iteration += 1
        
        if iteration == max_iterations:
            result = "Failed to converge"
        else:
            result = max(0, sip)  # Ensure non-negative result

    elif output_variable == 'stepup_percentage':
        corpus = inputs['corpus']
        principal = inputs['initial_investment']
        rate = inputs['rate_of_return'] / 100
        time = inputs['years']
        sip = inputs['sip_amount']
        
        # This calculation is complex and would require numerical methods for precision
        # Here's a simplified approximation
        monthly_rate = rate / 12
        months = int(time * 12)
        
        # Function to calculate future value of SIP with step-up
        def future_value_with_stepup(step_up_percentage):
            current_sip = sip
            future_value_sip = 0
            for year in range(int(time)):
                annual_sip = current_sip * 12
                future_value_sip += annual_sip * (1 + monthly_rate) ** ((time - year) * 12)
                current_sip *= (1 + step_up_percentage)
            return future_value_sip
        
        # Function to minimize: difference between future value and corpus
        def difference(step_up_percentage):
            return future_value_with_stepup(step_up_percentage) - corpus
        
        # Numerical derivative of the difference function
        def derivative(f, x, h=1e-5):
            return (f(x + h) - f(x - h)) / (2 * h)
        
        # Newton-Raphson method to find the step-up percentage
        step_up_percentage = 0.05  # Initial guess (5%)
        tolerance = 1e-6
        max_iterations = 100
        
        for i in range(max_iterations):
            f_value = difference(step_up_percentage)
            f_derivative = derivative(difference, step_up_percentage)
            
            if abs(f_value) < tolerance:
                break  # Stop if we're close enough to the root
            
            step_up_percentage = step_up_percentage - f_value / f_derivative
        
        if abs(f_value) < tolerance:
            result = step_up_percentage * 100  # Convert to percentage
        else:
            result = "Solution did not converge"    
    

    return round(result, 2) if result is not None else "Calculation not implemented"

# Streamlit web app

st.title('Smart Investment Calculator')

output_variable = st.selectbox('Output:', [
    'Expected Corpus',
    'Initial Investment',
    'Rate of Return',
    'Number of Years',
    'SIP Amount',
    'Step-up Percentage'
])

# Conditional rendering based on the selected output variable
corpus = st.number_input('Expected Corpus:', min_value=0) if output_variable != 'Expected Corpus' else 0
initial_investment = st.number_input('Initial Investment:', min_value=0) if output_variable != 'Initial Investment' else 0
rate_of_return = st.number_input('Rate of Return (%):', min_value=0.0) if output_variable != 'Rate of Return' else 0
years = st.number_input('Years:', min_value=0) if output_variable != 'Number of Years' else 0
sip_amount = st.number_input('SIP Amount:', min_value=0) if output_variable != 'SIP Amount' else 0
stepup_percentage = st.number_input('Step-up (%):', min_value=0.0) if output_variable != 'Step-up Percentage' else 0


inputs = {
    'initial_investment': initial_investment,
    'rate_of_return': rate_of_return,
    'years': years,
    'sip_amount': sip_amount,
    'stepup_percentage': stepup_percentage,
    'corpus': corpus,
}

# Mapping of output variable to input keys
output_variable_mapping = {
    'Expected Corpus': 'corpus',
    'Initial Investment': 'initial_investment',
    'Rate of Return': 'rate_of_return',
    'Number of Years': 'years',
    'SIP Amount': 'sip_amount',
    'Step-up Percentage': 'stepup_percentage'
}

if st.button('Calculate'):
    # Use the mapping to get the correct key for the output variable
    output_key = output_variable_mapping[output_variable]
    result = calculate_financial(output_key, **inputs)
    st.write(f"Result: {result}")

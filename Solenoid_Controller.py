from pyfirmata import Arduino, util
import time
import panel as pn
pn.extension()


class SolenoidController:
    def __init__(self, port):
        # Initialize the connection to the Arduino
        # 'port' is the serial port to which your Arduino is connected.
        self.board = Arduino(port)
        
        # Start an iterator thread so that serial buffer doesn't overflow
        self.it = util.Iterator(self.board)
        self.it.start()
        
        # Define the solenoid pin (digital pin 7 as output)
        self.solenoid_pin = self.board.get_pin('d:7:o')

    def open_solenoid(self):
        """Sets the solenoid pin to HIGH, opening the solenoid."""
        self.solenoid_pin.write(1)
        print("Solenoid opened")

    def close_solenoid(self):
        """Sets the solenoid pin to LOW, closing the solenoid"""
        self.solenoid_pin.write(0)
        print("Solenoid closed")
        
    def droplet(self):
        """Creates a droplet effect by opening and then quickly closing the solenoid"""
        self.open_solenoid()
        time.sleep(0.5)  # Wait for 125 milliseconds
        self.close_solenoid()
        print("Droplet created")

# Text box to display the current status
class SolenoidApp:
    def __init__(self, path_to_solenoid='/dev/cu.usbmodem143401'):
        self.status_text = pn.widgets.StaticText(value='Waiting')
        
        self.priming_toggle = pn.widgets.Toggle(name='Priming', button_type='success')
        self.priming_toggle.param.watch(self.toggle_priming, 'value')
        
        self.droplet_button = pn.widgets.Button(name='Droplet', button_type='primary')
        self.droplet_button.on_click(self.on_droplet_click)
        
        # Assuming the SolenoidController is already defined and instantiated
        self.solenoid_controller = SolenoidController(path_to_solenoid)
        
        
        self.layout = pn.Column(
            self.priming_toggle,
            self.droplet_button,
            self.status_text,
        )

    def update_status(self, new_status):
        self.status_text.value = new_status

    def toggle_priming(self, event):
        if event.new:
            self.solenoid_controller.open_solenoid()
            self.update_status('Priming')
            self.droplet_button.disabled = True
        else:
            
            self.solenoid_controller.close_solenoid()
            self.update_status('Waiting')
            self.droplet_button.disabled = False

    def on_droplet_click(self, event):
        self.update_status('Dropping')
        self.solenoid_controller.droplet()
        self.update_status('Waiting')

    def serve(self):
        return self.layout.servable()

# To serve the app, you would create an instance of SolenoidApp and call its serve method
solenoid_controller = SolenoidController('/dev/cu.usbmodem143401')
app = SolenoidApp()
app.serve()
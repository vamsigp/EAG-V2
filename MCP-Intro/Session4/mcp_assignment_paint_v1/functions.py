# basic import 
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp import types
from PIL import Image as PILImage
import math
import sys
from pywinauto.application import Application
import win32gui
import win32con
import time
from win32api import GetSystemMetrics

# instantiate an MCP server client
mcp = FastMCP("PaintMCP")

# Global handle for Paint application instance
paint_app = None
last_rectangle = None  # (x1, y1, x2, y2) normalized to top-left -> bottom-right

# DEFINE TOOLS

#addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    print("CALLED: add(a: int, b: int) -> int:")
    return int(a + b)

@mcp.tool()
def add_list(l: list) -> int:
    """Add all numbers in a list"""
    print("CALLED: add(l: list) -> int:")
    return sum(l)

# subtraction tool
@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    print("CALLED: subtract(a: int, b: int) -> int:")
    return int(a - b)

# multiplication tool
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    print("CALLED: multiply(a: int, b: int) -> int:")
    return int(a * b)

#  division tool
@mcp.tool() 
def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    print("CALLED: divide(a: int, b: int) -> float:")
    return float(a / b)

# power tool
@mcp.tool()
def power(a: int, b: int) -> int:
    """Power of two numbers"""
    print("CALLED: power(a: int, b: int) -> int:")
    return int(a ** b)

# square root tool
@mcp.tool()
def sqrt(a: int) -> float:
    """Square root of a number"""
    print("CALLED: sqrt(a: int) -> float:")
    return float(a ** 0.5)

# cube root tool
@mcp.tool()
def cbrt(a: int) -> float:
    """Cube root of a number"""
    print("CALLED: cbrt(a: int) -> float:")
    return float(a ** (1/3))

# factorial tool
@mcp.tool()
def factorial(a: int) -> int:
    """factorial of a number"""
    print("CALLED: factorial(a: int) -> int:")
    return int(math.factorial(a))

# log tool
@mcp.tool()
def log(a: int) -> float:
    """log of a number"""
    print("CALLED: log(a: int) -> float:")
    return float(math.log(a))

# remainder tool
@mcp.tool()
def remainder(a: int, b: int) -> int:
    """remainder of two numbers divison"""
    print("CALLED: remainder(a: int, b: int) -> int:")
    return int(a % b)

# sin tool
@mcp.tool()
def sin(a: int) -> float:
    """sin of a number"""
    print("CALLED: sin(a: int) -> float:")
    return float(math.sin(a))

# cos tool
@mcp.tool()
def cos(a: int) -> float:
    """cos of a number"""
    print("CALLED: cos(a: int) -> float:")
    return float(math.cos(a))

# tan tool
@mcp.tool()
def tan(a: int) -> float:
    """tan of a number"""
    print("CALLED: tan(a: int) -> float:")
    return float(math.tan(a))

# mine tool
@mcp.tool()
def mine(a: int, b: int) -> int:
    """special mining tool"""
    print("CALLED: mine(a: int, b: int) -> int:")
    return int(a - b - b)

@mcp.tool()
def create_thumbnail(image_path: str) -> Image:
    """Create a thumbnail from an image"""
    print("CALLED: create_thumbnail(image_path: str) -> Image:")
    img = PILImage.open(image_path)
    img.thumbnail((100, 100))
    return Image(data=img.tobytes(), format="png")

@mcp.tool()
def strings_to_chars_to_int(string: str) -> list[int]:
    """Return the ASCII values of the characters in a word"""
    print("CALLED: strings_to_chars_to_int(string: str) -> list[int]:")
    return [int(ord(char)) for char in string]

@mcp.tool()
def int_list_to_exponential_sum(int_list: list) -> float:
    """Return sum of exponentials of numbers in a list"""
    print("CALLED: int_list_to_exponential_sum(int_list: list) -> float:")
    return sum(math.exp(i) for i in int_list)

@mcp.tool()
def fibonacci_numbers(n: int) -> list:
    """Return the first n Fibonacci Numbers"""
    print("CALLED: fibonacci_numbers(n: int) -> list:")
    if n <= 0:
        return []
    fib_sequence = [0, 1]
    for _ in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence[:n]


@mcp.tool()
async def draw_rectangle(x1: int, y1: int, x2: int, y2: int) -> dict:
    """Draw a rectangle in Paint from (x1,y1) to (x2,y2)"""
    global paint_app, last_rectangle
    try:
        if not paint_app:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Paint is not open. Please call open_paint first."
                    )
                ]
            }
        
        # Get the Paint window
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Ensure Paint window is active
        if not paint_window.has_focus():
            paint_window.set_focus()
            time.sleep(0.2)
        
        # Select Rectangle tool (toolbar coordinates may vary by DPI/theme)
        # These coordinates target the Shapes -> Rectangle icon in modern MSPaint
        paint_window.click_input(coords=(440, 63))
        time.sleep(0.2)
        
        # Get the canvas area
        canvas = paint_window.child_window(class_name='MSPaintView')
        
        # Normalize coordinates to top-left and bottom-right
        tlx, tly = min(x1, x2), min(y1, y2)
        brx, bry = max(x1, x2), max(y1, y2)

        # Draw rectangle - start at top-left and drag to bottom-right
        canvas.press_mouse_input(coords=(tlx, tly))
        time.sleep(0.05)
        canvas.move_mouse_input(coords=(brx, bry))
        time.sleep(0.05)
        canvas.release_mouse_input(coords=(brx, bry))

        # Remember last rectangle
        last_rectangle = (tlx, tly, brx, bry)
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Rectangle drawn from ({tlx},{tly}) to ({brx},{bry})"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error drawing rectangle: {str(e)}"
                )
            ]
        }

@mcp.tool()
async def add_text_in_paint(text: str) -> dict:
    """Add text in Paint"""
    global paint_app
    try:
        if not paint_app:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Paint is not open. Please call open_paint first."
                    )
                ]
            }
        
        # Get the Paint window
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Ensure Paint window is active
        if not paint_window.has_focus():
            paint_window.set_focus()
            time.sleep(0.5)
        
        # Select Text tool (toolbar coordinates may vary by DPI/theme)
        paint_window.click_input(coords=(290, 70))
        time.sleep(0.5)
        
        # Get the canvas area
        canvas = paint_window.child_window(class_name='MSPaintView')
        
        # Click on canvas to place text box (generic position)
        canvas.click_input(coords=(150, 300))
        time.sleep(0.5)
        
        
        # Type the text passed from client
        paint_window.type_keys(text, with_spaces=True, pause=0.02)
    
        time.sleep(0.5)
        
        # Click to exit text mode
        canvas.click_input(coords=(1050, 800))
    
      
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Text:'{text}' added successfully"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )
            ]
        }

@mcp.tool()
async def get_last_rectangle_center() -> dict:
    """Get the center coordinates (x,y) of the last drawn rectangle"""
    global last_rectangle
    try:
        if not last_rectangle:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="No rectangle found. Draw a rectangle first."
                    )
                ]
            }

        x1, y1, x2, y2 = last_rectangle
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)
        return {
            "content": [
                TextContent(type="text", text=f"{cx},{cy}")
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(type="text", text=f"Error: {str(e)}")
            ]
        }

@mcp.tool()
async def add_text_in_paint_at(text: str, x: int, y: int) -> dict:
    """Add text in Paint at provided canvas coordinates (x,y)"""
    global paint_app
    try:
        if not paint_app:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Paint is not open. Please call open_paint first."
                    )
                ]
            }

        paint_window = paint_app.window(class_name='MSPaintApp')

        if not paint_window.has_focus():
            paint_window.set_focus()
            time.sleep(0.3)

        # Select Text tool
        paint_window.click_input(coords=(290, 70))
        time.sleep(0.3)

        canvas = paint_window.child_window(class_name='MSPaintView')
        canvas.click_input(coords=(x, y))
        time.sleep(0.3)

        paint_window.type_keys(text, with_spaces=True, pause=0.02)
        time.sleep(0.3)

        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Text:'{text}' added at ({x},{y})"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(type="text", text=f"Error: {str(e)}")
            ]
        }

@mcp.tool()
async def add_text_inside_last_rectangle(text: str) -> dict:
    """Create a text box constrained within the last drawn rectangle and type text"""
    global paint_app, last_rectangle
    try:
        if not paint_app:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Paint is not open. Please call open_paint first."
                    )
                ]
            }
        if not last_rectangle:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="No rectangle found. Draw a rectangle first."
                    )
                ]
            }

        x1, y1, x2, y2 = last_rectangle
        # Apply small margins to ensure the text box stays inside the border
        margin = 10
        left = x1 + margin
        top = y1 + margin
        right = max(left + 40, x2 - margin)
        bottom = max(top + 20, y2 - margin)

        paint_window = paint_app.window(class_name='MSPaintApp')
        if not paint_window.has_focus():
            paint_window.set_focus()
            time.sleep(0.3)

        # Select Text tool
        paint_window.click_input(coords=(290, 70))
        time.sleep(0.3)

        canvas = paint_window.child_window(class_name='MSPaintView')
        # Drag to create a text box within the rectangle bounds
        canvas.press_mouse_input(coords=(left, top))
        time.sleep(0.05)
        canvas.move_mouse_input(coords=(right, bottom))
        time.sleep(0.05)
        canvas.release_mouse_input(coords=(right, bottom))
        time.sleep(0.2)

        paint_window.type_keys(text, with_spaces=True, pause=0.02)
        time.sleep(0.3)

        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Text inserted inside rectangle ({x1},{y1})-({x2},{y2})"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(type="text", text=f"Error: {str(e)}")
            ]
        }

@mcp.tool()
async def open_paint() -> dict:
    """Open Microsoft Paint maximized on secondary monitor"""
    global paint_app
    try:
        paint_app = Application().start('mspaint.exe')
        time.sleep(0.2)
        
        # Get the Paint window
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Maximize the window
        win32gui.ShowWindow(paint_window.handle, win32con.SW_MAXIMIZE)
        # Bring to foreground explicitly
        try:
            win32gui.SetForegroundWindow(paint_window.handle)
        except Exception:
            pass
        time.sleep(0.2)
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text="Paint opened successfully and maximized"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error opening Paint: {str(e)}"
                )
            ]
        }
# DEFINE RESOURCES

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    print("CALLED: get_greeting(name: str) -> str:")
    return f"Hello, {name}!"


# DEFINE AVAILABLE PROMPTS
@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"
    print("CALLED: review_code(code: str) -> str:")


@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

if __name__ == "__main__":
    # Check if running with mcp dev command
    print("STARTING THE SERVER AT AMAZING LOCATION")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution

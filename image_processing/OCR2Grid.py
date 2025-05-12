from tabulate import tabulate
class OCR2Grid:
    def __init__(self, ocr_data,squares):
        self.ocr_data = ocr_data
        self.grid = [["" for _ in range(10)] for _ in range(16)]
        self.squares = squares
    
    def fill_grid(self):
        for square in self.squares:
            # Get the square's bounding box from its corners
            corners = square.corners
            square_x_min = min(c[0] for c in corners)
            square_x_max = max(c[0] for c in corners)
            square_y_min = min(c[1] for c in corners)
            square_y_max = max(c[1] for c in corners)

            for ocr in self.ocr_data:
                ocr_corners = ocr['corners']

                # Compute the center of the OCR bounding box
                center_x = sum(c[0] for c in ocr_corners) / 4
                center_y = sum(c[1] for c in ocr_corners) / 4

                # Check if center is inside the square bounding box
                if (square_x_min <= center_x <= square_x_max and
                    square_y_min <= center_y <= square_y_max):
                    self.grid[square.row][square.col] = ocr['text']
                    break

        return self.grid
  
    
    def print_grid(self):
        print(tabulate(self.grid, tablefmt="grid"))

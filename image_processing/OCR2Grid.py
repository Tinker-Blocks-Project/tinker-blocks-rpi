from tabulate import tabulate
class OCR2Grid:
    def __init__(self, ocr_data,squares):
        self.ocr_data = ocr_data
        self.grid = [["" for _ in range(10)] for _ in range(16)]
        self.squares = squares
    
    def fill_grid(self):
        for square in self.squares:
            # Get the square's corners
            corners = square.corners
            square_x_min = min(c[0] for c in corners)
            square_x_max = max(c[0] for c in corners)
            square_y_min = min(c[1] for c in corners)
            square_y_max = max(c[1] for c in corners)

            # Check each OCR item
            for ocr in self.ocr_data:
                ocr_corners = ocr['corners']
                ocr_x_min = min(c[0] for c in ocr_corners)
                ocr_x_max = max(c[0] for c in ocr_corners)
                ocr_y_min = min(c[1] for c in ocr_corners)
                ocr_y_max = max(c[1] for c in ocr_corners)

                # Check if the entire OCR box is within the square
                if (square_x_min <= ocr_x_min and ocr_x_max <= square_x_max and
                    square_y_min <= ocr_y_min and ocr_y_max <= square_y_max):
                    self.grid[square.row][square.col] = ocr['text']
                    break

        return self.grid    
    
    def print_grid(self):
        print(tabulate(self.grid, tablefmt="grid"))

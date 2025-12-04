# Design Document

## Overview

API SketchPad is a desktop application built with PyQt6 that provides a three-panel interface for managing API interactions. The application follows the Model-View-Controller (MVC) architectural pattern, with clear separation between data models, UI components, and business logic. The design emphasizes modularity, testability, and extensibility for future enhancements.

## Architecture

### High-Level Architecture

The application follows a layered architecture:

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                   │
│  (PyQt6 Widgets: MainWindow, Panels, Editors, Tables)   │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   Application Layer                     │
│     (Controllers, Event Handlers, Validators)           │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                      Domain Layer                       │
│        (Data Models, Business Logic, Serializers)       │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   Persistence Layer                     │
│          (JSON Serialization, File I/O)                 │
└─────────────────────────────────────────────────────────┘
```

### Design Patterns

1. **Model-View-Controller (MVC)**: Separates data (models), presentation (views), and logic (controllers)
2. **Observer Pattern**: UI components observe model changes and update automatically
3. **Repository Pattern**: Abstracts data persistence operations
4. **Factory Pattern**: Creates UI components and model instances
5. **Command Pattern**: Encapsulates user actions for undo/redo support (future)

## Components and Interfaces

### 1. Data Models

#### Interaction Model
```python
class Interaction:
    """Represents a single API interaction configuration."""
    
    def __init__(self):
        self.name: str
        self.description: str
        self.method: str  # GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS
        self.path: str
        self.request_headers: Dict[str, str]
        self.request_body: str
        self.responses: Dict[int, Response]  # status_code -> Response
    
    def to_dict(self) -> dict
    def from_dict(data: dict) -> Interaction
    def validate(self) -> List[str]  # Returns validation errors
```

#### Response Model
```python
class Response:
    """Represents an expected response for a specific status code."""
    
    def __init__(self):
        self.status_code: int
        self.headers: Dict[str, str]
        self.body: str
    
    def to_dict(self) -> dict
    def from_dict(data: dict) -> Response
```

#### InteractionRepository
```python
class InteractionRepository:
    """Manages the collection of interactions."""
    
    def __init__(self):
        self.interactions: List[Interaction]
        self.current_interaction: Optional[Interaction]
    
    def add_interaction(self, interaction: Interaction) -> None
    def remove_interaction(self, interaction: Interaction) -> None
    def get_interaction(self, index: int) -> Interaction
    def set_current_interaction(self, interaction: Interaction) -> None
    def export_to_file(self, filepath: str) -> None
    def import_from_file(self, filepath: str) -> None
```

### 2. UI Components

#### MainWindow
```python
class MainWindow(QMainWindow):
    """Main application window with three-panel layout."""
    
    def __init__(self):
        self.navigation_panel: NavigationPanel
        self.request_panel: RequestPanel
        self.response_panel: ResponsePanel
        self.repository: InteractionRepository
    
    def setup_ui(self) -> None
    def setup_splitters(self) -> None
    def setup_menu_bar(self) -> None
    def setup_keyboard_shortcuts(self) -> None
```

#### NavigationPanel
```python
class NavigationPanel(QWidget):
    """Left panel displaying list of interactions."""
    
    interaction_selected = pyqtSignal(Interaction)
    
    def __init__(self, repository: InteractionRepository):
        self.interaction_list: QListWidget
        self.add_button: QPushButton
        self.repository: InteractionRepository
    
    def refresh_list(self) -> None
    def on_add_interaction(self) -> None
    def on_interaction_selected(self, item: QListWidgetItem) -> None
```

#### RequestPanel
```python
class RequestPanel(QWidget):
    """Middle panel for configuring HTTP requests."""
    
    interaction_updated = pyqtSignal(Interaction)
    
    def __init__(self):
        self.name_field: QLineEdit
        self.description_field: QTextEdit
        self.method_dropdown: QComboBox
        self.path_field: QLineEdit
        self.headers_table: HeadersTableWidget
        self.body_editor: SyntaxHighlightEditor
        self.current_interaction: Optional[Interaction]
    
    def load_interaction(self, interaction: Interaction) -> None
    def save_to_interaction(self) -> None
    def on_name_changed(self, text: str) -> None
    def on_method_changed(self, method: str) -> None
```

#### ResponsePanel
```python
class ResponsePanel(QWidget):
    """Right panel for defining expected responses and testing."""
    
    def __init__(self):
        self.status_tabs: QTabWidget
        self.response_editors: Dict[int, ResponseEditor]
        self.try_it_section: TryItOutWidget
        self.current_interaction: Optional[Interaction]
    
    def load_interaction(self, interaction: Interaction) -> None
    def add_status_tab(self, status_code: int) -> None
    def remove_status_tab(self, status_code: int) -> None
    def on_tab_changed(self, index: int) -> None
```

#### SyntaxHighlightEditor
```python
class SyntaxHighlightEditor(QTextEdit):
    """Text editor with JSON/XML syntax highlighting."""
    
    def __init__(self):
        self.highlighter: SyntaxHighlighter
        self.format: str  # 'json' or 'xml'
    
    def set_format(self, format: str) -> None
    def get_text(self) -> str
    def set_text(self, text: str) -> None
```

#### HeadersTableWidget
```python
class HeadersTableWidget(QWidget):
    """Table widget for managing HTTP headers."""
    
    headers_changed = pyqtSignal(dict)
    
    def __init__(self):
        self.table: QTableWidget
        self.add_button: QPushButton
        self.remove_button: QPushButton
    
    def set_headers(self, headers: Dict[str, str]) -> None
    def get_headers(self) -> Dict[str, str]
    def on_add_header(self) -> None
    def on_remove_header(self) -> None
```

#### TryItOutWidget
```python
class TryItOutWidget(QWidget):
    """Widget for executing live API calls."""
    
    def __init__(self):
        self.endpoint_field: QLineEdit
        self.method_dropdown: QComboBox
        self.send_button: QPushButton
        self.response_preview: QTextEdit
        self.status_label: QLabel
        self.current_interaction: Optional[Interaction]
    
    def load_interaction(self, interaction: Interaction) -> None
    def on_send_clicked(self) -> None
    def display_response(self, response: SimulatedResponse) -> None
```

### 3. Controllers and Services

#### InteractionController
```python
class InteractionController:
    """Coordinates interactions between UI and data models."""
    
    def __init__(self, repository: InteractionRepository):
        self.repository: InteractionRepository
    
    def create_interaction(self) -> Interaction
    def update_interaction(self, interaction: Interaction) -> None
    def delete_interaction(self, interaction: Interaction) -> None
    def select_interaction(self, interaction: Interaction) -> None
```

#### APISimulator
```python
class APISimulator:
    """Simulates API calls for testing."""
    
    def execute_request(
        self,
        method: str,
        endpoint: str,
        headers: Dict[str, str],
        body: str
    ) -> SimulatedResponse
    
    def simulate_delay(self) -> None
```

#### ValidationService
```python
class ValidationService:
    """Validates user inputs and data."""
    
    @staticmethod
    def validate_json(text: str) -> Tuple[bool, Optional[str]]
    
    @staticmethod
    def validate_xml(text: str) -> Tuple[bool, Optional[str]]
    
    @staticmethod
    def validate_url_path(path: str) -> Tuple[bool, Optional[str]]
    
    @staticmethod
    def validate_header_key(key: str) -> Tuple[bool, Optional[str]]
```

#### SerializationService
```python
class SerializationService:
    """Handles JSON serialization/deserialization."""
    
    @staticmethod
    def serialize_interactions(interactions: List[Interaction]) -> str
    
    @staticmethod
    def deserialize_interactions(json_str: str) -> List[Interaction]
    
    @staticmethod
    def export_to_file(interactions: List[Interaction], filepath: str) -> None
    
    @staticmethod
    def import_from_file(filepath: str) -> List[Interaction]
```

## Data Models

### Interaction Data Structure

```json
{
  "name": "Get User Profile",
  "description": "Retrieves user profile information by user ID",
  "method": "GET",
  "path": "/api/users/{id}",
  "request_headers": {
    "Authorization": "Bearer ${API_TOKEN}",
    "Accept": "application/json"
  },
  "request_body": "",
  "responses": {
    "200": {
      "headers": {
        "Content-Type": "application/json"
      },
      "body": "{\n  \"id\": 123,\n  \"name\": \"John Doe\"\n}"
    },
    "404": {
      "headers": {
        "Content-Type": "application/json"
      },
      "body": "{\n  \"error\": \"User not found\"\n}"
    }
  }
}
```

### Collection Data Structure

```json
{
  "version": "1.0",
  "interactions": [
    {
      "name": "...",
      "description": "...",
      ...
    }
  ]
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Adding interaction increases collection size
*For any* collection of interactions, adding a new interaction should increase the collection size by exactly one and the new interaction should have the name "New Interaction"
**Validates: Requirements 1.1**

### Property 2: Selected interaction loads correctly
*For any* interaction in the repository, selecting that interaction should result in the Request Panel and Response Panel displaying that interaction's exact configuration data
**Validates: Requirements 1.2**

### Property 3: Name changes synchronize to navigation
*For any* interaction and any new name string, modifying the interaction name in the Request Panel should update the corresponding entry in the Navigation Panel to display the new name
**Validates: Requirements 1.3, 2.4**

### Property 4: Name field accepts valid lengths
*For any* string with length ≤ 255 characters, the interaction name field should accept the entire string; for any string with length > 255 characters, the field should truncate or reject the input
**Validates: Requirements 2.1**

### Property 5: Description field accepts unlimited text
*For any* string including very large strings (100,000+ characters), the interaction description field should accept and store the entire string without truncation
**Validates: Requirements 2.2**

### Property 6: New interactions initialize with empty fields
*For any* newly created interaction, both the name and description fields should be initialized as empty strings
**Validates: Requirements 2.3**

### Property 7: Description preserves formatting
*For any* string containing special characters, newlines, tabs, or other formatting, entering it in the description field should preserve the exact string including all formatting characters
**Validates: Requirements 2.5**

### Property 8: Valid HTTP methods accepted
*For any* HTTP method in the set {GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS}, setting that method on an interaction should succeed; for any string not in this set, setting the method should fail
**Validates: Requirements 3.1**

### Property 9: New interactions default to GET
*For any* newly created interaction, the HTTP method should be initialized to "GET"
**Validates: Requirements 3.2**

### Property 10: Valid URL paths accepted
*For any* valid URL path string (including paths with parameters like `/users/{id}`), the endpoint path field should accept the string
**Validates: Requirements 3.3**

### Property 11: Interaction data persists across switches
*For any* two interactions with different configurations (method, path, headers, body), switching from one to the other and back should preserve each interaction's original configuration exactly
**Validates: Requirements 3.4, 3.5**

### Property 12: New interactions have default headers
*For any* newly created interaction, the request headers should be initialized with exactly two headers: "Content-Type: application/json" and "Accept: application/json"
**Validates: Requirements 4.1**

### Property 13: Adding headers increases header count
*For any* interaction and any non-empty header key with any value, adding the header should result in the headers collection containing that key-value pair
**Validates: Requirements 4.3**

### Property 14: Removing headers decreases header count
*For any* interaction with at least one header, removing a header should result in that header no longer being present in the headers collection
**Validates: Requirements 4.4**

### Property 15: Environment variable syntax preserved
*For any* header value containing the pattern `${VARIABLE_NAME}`, storing and retrieving the header should preserve the exact string including the `${...}` syntax
**Validates: Requirements 4.5**

### Property 16: Auto-indentation maintains nesting
*For any* request body with nested JSON or XML structure, pressing Enter at a given nesting level should result in the new line being indented to match the current nesting level
**Validates: Requirements 5.3**

### Property 17: Paste preserves content exactly
*For any* string, pasting it into the request body editor should result in the editor containing the exact same string with no modifications
**Validates: Requirements 5.4**

### Property 18: New interactions have default status codes
*For any* newly created interaction, the responses collection should contain exactly three status codes: 200, 400, and 500, each with empty body and headers
**Validates: Requirements 6.1**

### Property 19: Status code tabs display correct data
*For any* interaction with multiple status codes, selecting each status code tab should display the response body and headers specific to that status code
**Validates: Requirements 6.2, 7.1**

### Property 20: Adding status codes creates empty responses
*For any* valid HTTP status code not already in an interaction's responses, adding that status code should create a response entry with empty body and empty headers
**Validates: Requirements 6.3**

### Property 21: Removing status codes deletes configuration
*For any* interaction with a status code in its responses, removing that status code should result in it no longer being present in the responses collection
**Validates: Requirements 6.4**

### Property 22: Response modifications are isolated by status code
*For any* interaction with multiple status codes, modifying the response body or headers for one status code should not affect the response body or headers of any other status code
**Validates: Requirements 6.5, 7.2, 7.3**

### Property 23: API simulation uses correct parameters
*For any* interaction configuration (method, endpoint, headers, body), executing a simulated API call should use exactly those parameters
**Validates: Requirements 8.1**

### Property 24: Response preview displays all components
*For any* simulated API response, the response preview should display the status code, all headers, and the complete body
**Validates: Requirements 8.2**

### Property 25: JSON responses are formatted
*For any* valid JSON string in a simulated response body, the displayed response should be properly indented and formatted
**Validates: Requirements 8.4**

### Property 26: Try It Out endpoint isolation
*For any* interaction, modifying the endpoint in the Try It Out section should not modify the interaction's stored endpoint path
**Validates: Requirements 8.6**

### Property 27: Interactions stored in memory are retrievable
*For any* interaction added to the repository, that interaction should be retrievable from memory with all its data intact
**Validates: Requirements 10.1**

### Property 28: Serialization round-trip preserves data
*For any* collection of interactions, serializing to JSON and then deserializing should produce a collection equivalent to the original with all fields (name, description, method, path, request_headers, request_body, responses) preserved exactly
**Validates: Requirements 10.2, 10.3, 10.5**

### Property 29: Serialization includes all required fields
*For any* interaction, the serialized JSON should contain all required fields: name, description, method, path, request_headers, request_body, and responses
**Validates: Requirements 10.4**

### Property 30: Malformed JSON handled gracefully
*For any* malformed JSON string entered in a request or response body, the application should handle it without crashing and should display an error message
**Validates: Requirements 12.1**

### Property 31: Import errors preserve application state
*For any* invalid or corrupted JSON file, attempting to import should fail gracefully, display an error message, and leave the current collection of interactions unchanged
**Validates: Requirements 12.2**

### Property 32: Error messages include technical details
*For any* error condition, the error message should include technical details that can be used for debugging
**Validates: Requirements 12.5**

### Property 33: Header keys must be non-empty
*For any* empty string, attempting to use it as a header key should be rejected; for any non-empty string, it should be accepted as a valid header key
**Validates: Requirements 13.1**

### Property 34: URL path validation
*For any* string representing a valid URL path, the path validation should accept it; for any string that is not a valid URL path, the validation should reject it
**Validates: Requirements 13.2**

### Property 35: Invalid JSON allowed in body
*For any* string (valid or invalid JSON), entering it in the request body field should be accepted and stored
**Validates: Requirements 13.3**

### Property 36: Empty interaction names allowed
*For any* interaction, setting the name to an empty string should be accepted as valid
**Validates: Requirements 13.4**

### Property 37: Empty header values allowed
*For any* header, setting the value to an empty string should be accepted as valid
**Validates: Requirements 13.5**

## Error Handling

### Error Categories

1. **User Input Errors**
   - Malformed JSON/XML in request/response bodies
   - Invalid HTTP method selection
   - Invalid URL path syntax
   - Empty header keys

2. **File I/O Errors**
   - File not found during import
   - Permission denied during export
   - Corrupted JSON file during import
   - Disk full during export

3. **Application Errors**
   - Memory allocation failures
   - UI rendering errors
   - Thread synchronization issues

### Error Handling Strategy

#### Validation Errors
- Validate user input at the point of entry
- Display inline error messages near the input field
- Use red color (#F44336) for error indicators
- Provide specific guidance on how to fix the error
- Allow users to continue working with other parts of the application

#### File I/O Errors
- Wrap all file operations in try-except blocks
- Display modal dialog with error details
- Preserve application state on import failures
- Offer retry option for transient errors
- Log errors to application log file

#### Application Errors
- Catch all unhandled exceptions at the top level
- Display user-friendly error dialog
- Include technical details in expandable section
- Offer option to save current work before closing
- Log full stack trace for debugging

### Error Message Format

```python
class ErrorMessage:
    """Standard error message structure."""
    
    def __init__(self):
        self.title: str  # Short error title
        self.message: str  # User-friendly description
        self.technical_details: str  # Stack trace, error codes
        self.suggestions: List[str]  # How to resolve
        self.severity: str  # 'error', 'warning', 'info'
```

## Testing Strategy

### Unit Testing

The application will use **pytest** as the testing framework for unit tests. Unit tests will focus on:

1. **Data Model Tests**
   - Interaction creation and initialization
   - Response model creation
   - Data validation methods
   - Edge cases (empty strings, None values, very long strings)

2. **Serialization Tests**
   - JSON serialization of interactions
   - JSON deserialization of interactions
   - Handling of special characters
   - Error handling for corrupted data

3. **Validation Tests**
   - URL path validation
   - Header key validation
   - HTTP method validation
   - JSON/XML syntax validation

4. **Repository Tests**
   - Adding/removing interactions
   - Retrieving interactions
   - Current interaction management
   - Export/import functionality

### Property-Based Testing

The application will use **Hypothesis** as the property-based testing library. Property-based tests will verify universal properties across many randomly generated inputs.

**Configuration:**
- Each property-based test will run a minimum of 100 iterations
- Tests will use Hypothesis strategies to generate valid test data
- Each test will be tagged with a comment referencing the design document property

**Property Test Structure:**
```python
from hypothesis import given, strategies as st

# Feature: api-sketchpad, Property 1: Adding interaction increases collection size
@given(st.lists(st.builds(Interaction)))
def test_adding_interaction_increases_size(interactions):
    """Test that adding an interaction increases collection size by one."""
    repository = InteractionRepository()
    for interaction in interactions:
        repository.add_interaction(interaction)
    
    initial_count = len(repository.interactions)
    repository.add_interaction(Interaction())
    
    assert len(repository.interactions) == initial_count + 1
    assert repository.interactions[-1].name == "New Interaction"
```

**Hypothesis Strategies:**
- `interaction_strategy`: Generates random Interaction objects
- `header_dict_strategy`: Generates random header dictionaries
- `http_method_strategy`: Generates valid HTTP methods
- `url_path_strategy`: Generates valid URL paths
- `json_string_strategy`: Generates valid JSON strings
- `status_code_strategy`: Generates valid HTTP status codes

### Integration Testing

Integration tests will verify that components work together correctly:

1. **UI-Model Integration**
   - Verify that UI changes update the model
   - Verify that model changes update the UI
   - Test signal/slot connections

2. **Panel Synchronization**
   - Test that selecting an interaction updates all panels
   - Test that modifying data in one panel updates other panels
   - Test that switching interactions preserves data

3. **Import/Export Workflow**
   - Test complete export-import cycle
   - Test importing into non-empty repository
   - Test error handling during import/export

### Test Organization

```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_serialization.py
│   ├── test_validation.py
│   └── test_repository.py
├── property/
│   ├── test_interaction_properties.py
│   ├── test_serialization_properties.py
│   ├── test_validation_properties.py
│   └── strategies.py
└── integration/
    ├── test_ui_integration.py
    ├── test_panel_sync.py
    └── test_import_export.py
```

### Test Coverage Goals

- Unit test coverage: 80% minimum
- Property test coverage: All 37 correctness properties
- Integration test coverage: All major workflows
- Critical paths: 100% coverage (serialization, data persistence)

## Implementation Notes

### PyQt6 Specific Considerations

1. **Signal/Slot Mechanism**
   - Use signals for loose coupling between components
   - Connect UI events to controller methods
   - Emit signals when model data changes

2. **Thread Safety**
   - Keep all UI updates on the main thread
   - Use QThread for long-running operations (future: real API calls)
   - Use QTimer for simulated delays

3. **Layout Management**
   - Use QSplitter for resizable columns
   - Use QVBoxLayout and QHBoxLayout for component arrangement
   - Set minimum sizes to prevent UI collapse

4. **Syntax Highlighting**
   - Implement QSyntaxHighlighter subclass
   - Use QRegularExpression for pattern matching
   - Apply QTextCharFormat for styling

### Performance Optimizations

1. **Lazy Loading**
   - Load interaction details only when selected
   - Defer syntax highlighting until text changes

2. **Efficient Updates**
   - Use blockSignals() to prevent cascading updates
   - Batch UI updates when loading interactions
   - Debounce text field updates

3. **Memory Management**
   - Limit undo/redo history size
   - Clear unused syntax highlighting data
   - Use weak references where appropriate

### Extensibility Points

1. **Plugin Architecture (Future)**
   - Define plugin interface for custom validators
   - Support custom syntax highlighters
   - Allow custom authentication handlers

2. **Configuration System (Future)**
   - User preferences (font size, color scheme)
   - Default headers and values
   - Keyboard shortcut customization

3. **Scripting Support (Future)**
   - Pre-request script execution
   - Post-response script execution
   - Environment variable management

## Dependencies

### Required Dependencies

```toml
[tool.poetry.dependencies]
python = "^3.8"
PyQt6 = "^6.4.0"
```

### Development Dependencies

```toml
[tool.poetry.dev-dependencies]
pytest = "^7.0.0"
pytest-qt = "^4.2.0"
hypothesis = "^6.0.0"
black = "^23.0.0"
mypy = "^1.0.0"
```

### Optional Dependencies

```toml
[tool.poetry.extras]
syntax = ["pygments"]  # Advanced syntax highlighting
http = ["requests"]     # Real API calls (future)
```

## Deployment

### Packaging

The application will be packaged using PyInstaller for distribution:

```bash
pyinstaller --name="API SketchPad" \
            --windowed \
            --icon=assets/icon.ico \
            --add-data="assets:assets" \
            main.py
```

### Platform-Specific Considerations

**Windows:**
- Create installer using NSIS or Inno Setup
- Include Visual C++ redistributables if needed
- Register file associations for .apisketch files

**macOS:**
- Create .app bundle with proper Info.plist
- Sign application with Apple Developer certificate
- Create DMG for distribution

**Linux:**
- Create .deb package for Debian/Ubuntu
- Create .rpm package for Fedora/RHEL
- Provide AppImage for universal compatibility

### Installation Script

A Makefile will provide convenient installation commands:

```makefile
install:
    pip install -e .

install-dev:
    pip install -e ".[dev]"

test:
    pytest tests/

test-property:
    pytest tests/property/ -v

run:
    python -m api_sketchpad

build:
    pyinstaller api_sketchpad.spec
```

## Future Enhancements

### Phase 2 Features

1. **Environment Variables**
   - Manage multiple environments (dev, staging, prod)
   - Variable substitution in headers and body
   - Environment-specific configurations

2. **Query Parameters**
   - Separate table for URL query parameters
   - Auto-generation of query string
   - Parameter validation

3. **Authentication Helpers**
   - OAuth2 flow support
   - Basic Auth dialog
   - API Key management
   - Token refresh handling

### Phase 3 Features

1. **OpenAPI Import**
   - Parse OpenAPI 3.0 specifications
   - Auto-generate interactions from endpoints
   - Sync with OpenAPI changes

2. **Collaboration**
   - Share collections via cloud storage
   - Team workspaces
   - Version control integration

3. **Advanced Testing**
   - Response assertions
   - Test suites and runners
   - Performance testing
   - Mock server generation

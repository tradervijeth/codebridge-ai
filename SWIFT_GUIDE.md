# Using CodeBridge AI for Swift and Xcode Development

This guide will help you leverage CodeBridge AI to accelerate your Swift app development and debug Xcode errors.

## Getting Started

### Initial Setup

1. **Set up Swift documentation**:
   ```bash
   cd /Users/vithushanjeyapahan/Documents/GitHub/codebridge-ai
   python run_swift_setup.py
   ```
   This will download Swift documentation, SwiftUI and UIKit references, and common error solutions.

2. **Ensure LM Studio is running**:
   - Open LM Studio
   - Load your GLM-4-0414 model
   - Enable the Local Server (Settings > Local Server > Enable)
   - Start the server

3. **Run CodeBridge AI**:
   ```bash
   python src/main.py
   ```

## Working with Xcode Errors

### Directly Process Xcode Errors

You can directly process Xcode error messages:

```bash
python src/xcode_helper.py --error "Cannot find 'ContentView' in scope"
```

For more complex errors with multiple lines, save them to a file:

```bash
python src/xcode_helper.py --error-file path/to/error.txt
```

### Common Error Workflow

1. When you encounter an error in Xcode:
   - Copy the error message
   - Run the helper with the error message
   - Review the suggested solution
   - Apply the fix to your code

### Integration with Xcode

For seamless integration, you can set up a simple script in your project:

1. Create a shell script named `debug.sh` in your project:
   ```bash
   #!/bin/bash
   
   # Save error to temporary file
   error_file="/tmp/xcode_error.txt"
   echo "$1" > "$error_file"
   
   # Process with CodeBridge AI
   cd /Users/vithushanjeyapahan/Documents/GitHub/codebridge-ai
   python src/xcode_helper.py --error-file "$error_file"
   ```

2. Make it executable:
   ```bash
   chmod +x debug.sh
   ```

3. Call it from Xcode:
   - In Xcode, go to Product > Scheme > Edit Scheme
   - Select "Build" and add a "Post-action" script
   - Add: `$PROJECT_DIR/debug.sh "${BUILD_LOG_PATH}"`

## Asking for Code Implementation

### Command Line Usage

To get suggestions for implementing a Swift feature:

```bash
python src/xcode_helper.py --implement "Create a SwiftUI view that displays a list of items with a custom cell design"
```

### Interactive Mode

For an interactive session with more context:

```bash
python src/main.py
```

Then type your Swift-related questions, for example:
- "How do I implement Core Data in a SwiftUI app?"
- "What's the best way to manage authentication in my iOS app?"
- "How can I implement infinite scrolling in a UITableView?"

## Swift-Specific Features

CodeBridge AI has been enhanced with Swift-specific capabilities:

1. **Error Detection**: Automatically detects Swift and Xcode error patterns
2. **Context-Aware Responses**: Provides solutions based on Swift best practices
3. **Code Examples**: Includes working Swift code examples in responses
4. **Documentation Awareness**: Has access to Swift, SwiftUI, and UIKit documentation

## Best Practices

1. **Be Specific**: The more detailed your question or error, the better the solution

2. **Include Context**: When possible, include relevant code around your error

3. **Iterative Approach**: Complex problems might need multiple queries to fully solve

4. **Keep Documentation Current**: Periodically run the setup script to update documentation:
   ```bash
   python run_swift_setup.py
   ```

## Example Use Cases

### Debugging Errors

```
> I'm getting "Value of type 'View' has no member 'cornerRadius'"

This error occurs because `cornerRadius()` is a modifier that needs to be applied to a specific View type, not to a protocol. The `View` protocol itself doesn't have this method.

The most likely cause is that you're trying to apply multiple modifiers, and the order is incorrect. In SwiftUI, the order of modifiers matters.

### Solution:

Make sure you're applying `cornerRadius()` to a concrete view or after other modifiers that return a concrete view:

```swift
// INCORRECT:
var body: some View {
    Text("Hello")
        .padding()
        .background(Color.blue)
    // At this point, we have a View protocol, not a concrete view
        .cornerRadius(10) // ERROR!
}

// CORRECT:
var body: some View {
    Text("Hello")
        .padding()
        .background(Color.blue)
        .clipShape(RoundedRectangle(cornerRadius: 10)) // This works!
}

// ALSO CORRECT (order matters):
var body: some View {
    Text("Hello")
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 10)
                .fill(Color.blue)
        )
}
```

In SwiftUI, many modifiers like `background()` return a View protocol type, not a specific View. The `cornerRadius()` modifier needs to be applied to specific view types, not to the View protocol itself.
```

### Implementation Suggestions

```
> Create a tab-based SwiftUI app with three screens

Here's a complete implementation of a tab-based SwiftUI app with three screens:

```swift
import SwiftUI

@main
struct TabBasedApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

struct ContentView: View {
    var body: some View {
        TabView {
            HomeView()
                .tabItem {
                    Label("Home", systemImage: "house")
                }
            
            ExploreView()
                .tabItem {
                    Label("Explore", systemImage: "safari")
                }
            
            ProfileView()
                .tabItem {
                    Label("Profile", systemImage: "person")
                }
        }
    }
}

// Home Screen
struct HomeView: View {
    var body: some View {
        NavigationView {
            VStack {
                Text("Home Screen")
                    .font(.largeTitle)
                    .padding()
                
                Text("Welcome to the app!")
                    .foregroundColor(.secondary)
            }
            .navigationTitle("Home")
        }
    }
}

// Explore Screen
struct ExploreView: View {
    let items = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]
    
    var body: some View {
        NavigationView {
            List(items, id: \.self) { item in
                NavigationLink(destination: DetailView(item: item)) {
                    Text(item)
                }
            }
            .navigationTitle("Explore")
        }
    }
}

// Detail View for Explore Items
struct DetailView: View {
    let item: String
    
    var body: some View {
        VStack {
            Text(item)
                .font(.largeTitle)
                .padding()
            
            Text("This is the detail view for \(item)")
                .foregroundColor(.secondary)
        }
        .navigationTitle(item)
    }
}

// Profile Screen
struct ProfileView: View {
    @State private var username = "SwiftUser"
    @State private var bio = "iOS Developer"
    @State private var isEditing = false
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("User Information")) {
                    if isEditing {
                        TextField("Username", text: $username)
                        TextField("Bio", text: $bio)
                    } else {
                        Text("Username: \(username)")
                        Text("Bio: \(bio)")
                    }
                }
            }
            .navigationTitle("Profile")
            .toolbar {
                Button(isEditing ? "Done" : "Edit") {
                    isEditing.toggle()
                }
            }
        }
    }
}

// Preview
struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
```

This implementation includes:

1. A main ContentView with a TabView for navigation
2. Three screens: Home, Explore, and Profile
3. Navigation within the Explore tab to show details
4. A simple editable profile screen
5. Appropriate icons and labels for the tab bar

To use this in your project:
- Create a new SwiftUI project in Xcode
- Replace the default ContentView.swift with this code
- Run the app to see the tab-based interface

You can customize each screen by adding your own content and functionality as needed.
```

## Troubleshooting

If you encounter issues:

1. **API Connection Issues**:
   - Ensure LM Studio is running and the server is started
   - Check the port number in LM Studio settings
   - Use `--lmstudio-url` parameter if needed

2. **No Documents Found**:
   - Ensure you've run the setup script
   - Check the `data/docs/swift` directory

3. **Poor or Incorrect Responses**:
   - Try rephrasing your question
   - Include more context or code
   - Use the specialized Xcode helper for errors

4. **Slow Responses**:
   - Consider using a smaller model in LM Studio
   - Reduce the number of returned context chunks in your query

## Need More Help?

If you need further assistance, feel free to open an issue in the CodeBridge AI repository or consult the main README.md file.

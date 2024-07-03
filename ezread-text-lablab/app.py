import streamlit as st
import os
import divider_text as div

# Define the directory to save the uploaded books
books_directory = 'books'

# Ensure the 'books' directory exists
if not os.path.exists(books_directory):
    os.makedirs(books_directory)

def upload_book():
    st.title("Import Book")
    
    # File uploader widget
    uploaded_file = st.file_uploader("Choose a book file", type=['docx'], key='file_uploader')
    
    if uploaded_file is not None:
        # Save the uploaded file to the 'books' directory
        file_path = os.path.join(books_directory, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File '{uploaded_file.name}' saved to '{books_directory}' folder.")

def view_books():
    st.title("View Books")
    
    # List all files in the 'books' directory
    files = os.listdir(books_directory)
    if files:
        st.write("Files in 'books' folder:")
        for idx, file in enumerate(files):
            if file == '1.txt':
                continue
            file_path = os.path.join(books_directory, file)
            if st.button(f"View {file}", key=f'view_{idx}'):
                # Call the divider function and get the segmented text
                text_segments = div.divider(file_path)
                
                # Initialize session state to keep track of which segment to show
                st.session_state.text_segments = text_segments
                st.session_state.segment_index = 0
                st.session_state.viewing_file = file
    
    # Display the text segments if a file is being viewed
    if 'viewing_file' in st.session_state and 'text_segments' in st.session_state:
        st.markdown(f"### Viewing: {st.session_state.viewing_file}")
        st.write(st.session_state.text_segments[st.session_state.segment_index])
        
        # Button to show the next segment
        if st.button("Next", key='next_segment'):
            if st.session_state.segment_index < len(st.session_state.text_segments) - 1:
                st.session_state.segment_index += 1
            else:
                st.session_state.segment_index = 0  # Reset to start when reaching the end
                

def main():
    st.sidebar.title("Navigation")
    tab = st.sidebar.radio("Select a tab", ("Import Book", "View Books"))

    if tab == "Import Book":
        upload_book()
    elif tab == "View Books":
        view_books()

if __name__ == "__main__":
    main()
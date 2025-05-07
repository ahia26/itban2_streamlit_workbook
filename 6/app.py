import cv2
import streamlit as st

# Initialize webcam
cap = cv2.VideoCapture(0)

# Streamlit UI
st.title("Real-Time Video Processing with Filters")

# Placeholder for video frames
frame_placeholder = st.empty()

# Sliders for filters
blur_amount = st.slider("Blur Amount", 1, 20, 5)
threshold1 = st.slider("Edge Detection Threshold 1", 0, 255, 50)
threshold2 = st.slider("Edge Detection Threshold 2", 0, 255, 150)

# Button to take a snapshot
snapshot_btn = st.button("Take Snapshot")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to RGB for Streamlit display
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Apply filters
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred_frame = cv2.GaussianBlur(frame, (blur_amount*2+1, blur_amount*2+1), 0)
    edge_frame = cv2.Canny(frame, threshold1, threshold2)

    # Display original and processed frames
    frame_placeholder.image(
        [frame_rgb, gray_frame, blurred_frame, edge_frame],
        caption=["Original", "Grayscale", "Blurred", "Edge Detection"],
        channels="RGB"
    )

    # Save snapshot
    if snapshot_btn:
        cv2.imwrite("snapshot.jpg", frame)
        st.success("Snapshot saved!")

    # Streamlit requires breaking the loop for updates
    break

# Release webcam
cap.release()
cv2.destroyAllWindows()
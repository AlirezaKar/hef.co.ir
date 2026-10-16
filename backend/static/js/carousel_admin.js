/**
 * Carousel Image Cropper for Django Admin
 * Uses Cropper.js for image cropping in the admin interface
 */

(function() {
    'use strict';

    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        initCarouselCropper();
    });

    function initCarouselCropper() {
        const imageInput = document.querySelector('.carousel-image-upload');
        if (!imageInput) return;

        // Create crop container
        const cropContainer = document.createElement('div');
        cropContainer.className = 'crop-container';
        cropContainer.style.display = 'none';

        const cropImage = document.createElement('img');
        cropImage.id = 'crop-image';
        cropImage.style.maxWidth = '100%';
        cropContainer.appendChild(cropImage);

        const cropActions = document.createElement('div');
        cropActions.className = 'crop-actions';

        const cropBtn = document.createElement('button');
        cropBtn.type = 'button';
        cropBtn.className = 'crop-btn crop-btn-primary';
        cropBtn.textContent = 'برش تصویر';
        cropBtn.id = 'crop-btn';

        const cancelBtn = document.createElement('button');
        cancelBtn.type = 'button';
        cancelBtn.className = 'crop-btn crop-btn-secondary';
        cancelBtn.textContent = 'انصراف';
        cancelBtn.id = 'cancel-crop-btn';
        cancelBtn.style.display = 'none';

        cropActions.appendChild(cropBtn);
        cropActions.appendChild(cancelBtn);
        cropContainer.appendChild(cropActions);

        // Insert after image input
        imageInput.parentNode.insertBefore(cropContainer, imageInput.nextSibling);

        let cropper = null;

        // Handle file selection
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function(event) {
                cropImage.src = event.target.result;
                cropContainer.style.display = 'block';
                cancelBtn.style.display = 'inline-block';

                // Initialize cropper
                if (cropper) {
                    cropper.destroy();
                }

                cropper = new Cropper(cropImage, {
                    aspectRatio: 16 / 9, // Default carousel aspect ratio
                    viewMode: 1,
                    dragMode: 'move',
                    autoCropArea: 0.8,
                    restore: false,
                    guides: true,
                    center: true,
                    highlight: false,
                    cropBoxMovable: true,
                    cropBoxResizable: true,
                    toggleDragModeOnDblclick: false,
                    responsive: true,
                });
            };
            reader.readAsDataURL(file);
        });

        // Handle crop button click
        cropBtn.addEventListener('click', function() {
            if (!cropper) return;

            // Get cropped canvas
            const canvas = cropper.getCroppedCanvas({
                width: 1920,
                height: 1080,
                imageSmoothingEnabled: true,
                imageSmoothingQuality: 'high',
            });

            if (canvas) {
                // Convert to blob and create new file
                canvas.toBlob(function(blob) {
                    const file = new File([blob], imageInput.files[0].name, {
                        type: 'image/jpeg',
                        lastModified: Date.now(),
                    });

                    // Create a new FileList
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(file);
                    imageInput.files = dataTransfer.files;

                    // Hide crop container
                    cropContainer.style.display = 'none';
                    cancelBtn.style.display = 'none';

                    // Destroy cropper
                    if (cropper) {
                        cropper.destroy();
                        cropper = null;
                    }

                    // Show success message
                    showNotification('تصویر با موفقیت برش داده شد', 'success');
                }, 'image/jpeg', 0.9);
            }
        });

        // Handle cancel button click
        cancelBtn.addEventListener('click', function() {
            cropContainer.style.display = 'none';
            cancelBtn.style.display = 'none';
            imageInput.value = '';

            if (cropper) {
                cropper.destroy();
                cropper = null;
            }
        });
    }

    function showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'crop-notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: ${type === 'success' ? '#28a745' : '#dc3545'};
            color: white;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            z-index: 9999;
            font-family: Tahoma, Arial, sans-serif;
            animation: slideIn 0.3s ease-out;
        `;

        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(function() {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(function() {
                notification.remove();
            }, 300);
        }, 3000);
    }

    // Add animation styles
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);

})();

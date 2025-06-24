import os
import sys
import platform
import pathlib
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon

class WorkerThread(QThread):
    progress = pyqtSignal(int)
    log_entry = pyqtSignal(str)
    finished = pyqtSignal(list, int)
    error = pyqtSignal(str)

    def __init__(self, folder1, folder2, prefix):
        super().__init__()
        self.folder1 = folder1
        self.folder2 = folder2
        self.prefix = prefix
    
    def run(self):
        try:
            log = []
            count = 0
            # Initialize log
            prefix_text = f'"{self.prefix}"' if self.prefix else 'none'
            log.append(f'Checking for missing images for ROMs in "{self.folder1}" against images in "{self.folder2}" with prefix {prefix_text}')
            self.log_entry.emit(f'Checking for missing images for ROMs in "{self.folder1}" against images in "{self.folder2}" with prefix {prefix_text}')
            log.append(f'Date: {datetime.now():%Y-%m-%d %H:%M:%S}')
            self.log_entry.emit(f'Date: {datetime.now():%Y-%m-%d %H:%M:%S}')
            log.append('============================================================')
            self.log_entry.emit('============================================================')

            # Get list of all files in folder1 (top-level) and .cue files in subfolders
            folder1_path = pathlib.Path(self.folder1)
            top_level_files = [f.name for f in folder1_path.iterdir() if f.is_file()]
            cue_files = [f for f in folder1_path.rglob('*.cue') if f.is_file()]
            # Combine and deduplicate
            all_files = list(set(top_level_files + [f.name for f in cue_files]))
            total_files = len(all_files)
            
            # Check for missing images
            folder2_path = pathlib.Path(self.folder2)
            image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}  # Common image extensions
            for i, file_name in enumerate(all_files):
                basename = os.path.splitext(file_name)[0]
                found = False
                
                # Search for matching image files in folder2 and its subfolders
                search_pattern = f'{self.prefix}{basename}.*' if self.prefix else f'{basename}.*'
                for img_file in folder2_path.rglob(search_pattern):
                    if img_file.is_file() and img_file.suffix.lower() in image_extensions:
                        found = True
                        break
                
                if not found:
                    log.append(f'MISSING: {self.prefix}{basename}')
                    self.log_entry.emit(f'MISSING: {self.prefix}{basename}')
                    count += 1
                
                # Update progress
                progress_percent = int((i + 1) / total_files * 100)
                self.progress.emit(progress_percent)
            
            # Summary
            log.append('')
            self.log_entry.emit('')
            log.append(f'TOTAL MISSING: {count} image(s)')
            self.log_entry.emit(f'TOTAL MISSING: {count} image(s)')
            log.append('============================================================')
            self.log_entry.emit('============================================================')
            log.append(f'Check completed at {datetime.now():%H:%M:%S}')
            self.log_entry.emit(f'Check completed at {datetime.now():%H:%M:%S}')
            
            self.finished.emit(log, count)
        except PermissionError as e:
            self.error.emit(f'Permission denied accessing files: {str(e)}')
        except Exception as e:
            self.error.emit(f'Error during check: {str(e)}')

class MissingImagesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.worker_thread = None
    
    def initUI(self):
        self.setWindowTitle('Check Missing Images')
        self.setGeometry(100, 100, 800, 600)
        
        if platform.system() == "Windows":
            icon_path = "cmi.ico"
        else:
            icon_path = "cmi.png" if os.path.isfile("cmi.png") else ""
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))
        
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Input fields
        input_layout = QVBoxLayout()
        
        # ROMs folder
        roms_layout = QHBoxLayout()
        roms_label = QLabel('ROMs Path:')
        roms_label.setFixedWidth(80)  # Align labels
        self.roms_input = QLineEdit()
        self.roms_input.setMinimumWidth(400)  # Ensure sufficient width
        roms_button = QPushButton('Browse ROMs')
        roms_button.setFixedWidth(120)  # Harmonize button width
        roms_button.clicked.connect(self.browse_roms)
        roms_layout.addWidget(roms_label)
        roms_layout.addWidget(self.roms_input)
        roms_layout.addWidget(roms_button)
        
        # Images folder
        images_layout = QHBoxLayout()
        images_label = QLabel('Images Path:')
        images_label.setFixedWidth(80)  # Align labels
        self.images_input = QLineEdit()
        self.images_input.setMinimumWidth(400)  # Ensure sufficient width
        images_button = QPushButton('Browse Images')
        images_button.setFixedWidth(120)  # Harmonize button width
        images_button.clicked.connect(self.browse_images)
        images_layout.addWidget(images_label)
        images_layout.addWidget(self.images_input)
        images_layout.addWidget(images_button)
        
        # Prefix (optional)
        prefix_layout = QHBoxLayout()
        prefix_label = QLabel('Prefix:')
        prefix_label.setFixedWidth(80)  # Align labels
        self.prefix_input = QLineEdit()
        self.prefix_input.setMinimumWidth(400)  # Ensure sufficient width
        self.prefix_input.setPlaceholderText('Optional')
        prefix_layout.addWidget(prefix_label)
        prefix_layout.addWidget(self.prefix_input)
        prefix_layout.addStretch()  # Push prefix input to align with others
        
        input_layout.addLayout(roms_layout)
        input_layout.addLayout(images_layout)
        input_layout.addLayout(prefix_layout)
        
        # Check button
        self.check_button = QPushButton('Check Missing Images')
        self.check_button.clicked.connect(self.check_missing)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        
        # Output display
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        
        # Save log button
        save_button = QPushButton('Save Log')
        save_button.clicked.connect(self.save_log)
        
        # Add all to main layout
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.check_button)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.output_text)
        main_layout.addWidget(save_button)
    
    def browse_roms(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select ROMs Folder')
        if folder:
            self.roms_input.setText(str(pathlib.Path(folder)))
    
    def browse_images(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Images Folder')
        if folder:
            self.images_input.setText(str(pathlib.Path(folder)))
    
    def check_missing(self):
        folder1 = self.roms_input.text()
        folder2 = self.images_input.text()
        prefix = self.prefix_input.text().strip()
        
        if not (folder1 and folder2):
            QMessageBox.warning(self, 'Error', 'Please fill in both folder paths.')
            return
        
        if not (pathlib.Path(folder1).is_dir() and pathlib.Path(folder2).is_dir()):
            QMessageBox.warning(self, 'Error', 'Invalid folder paths.')
            return
        
        # Disable check button to prevent multiple runs
        self.check_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.output_text.clear()
        
        # Start worker thread
        self.worker_thread = WorkerThread(folder1, folder2, prefix)
        self.worker_thread.progress.connect(self.update_progress)
        self.worker_thread.log_entry.connect(self.update_log)
        self.worker_thread.finished.connect(self.check_finished)
        self.worker_thread.error.connect(self.handle_error)
        self.worker_thread.start()
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    def update_log(self, entry):
        self.output_text.append(entry)
    
    def check_finished(self, log, count):
        self.log = log
        self.check_button.setEnabled(True)
        self.progress_bar.setValue(100)
        QMessageBox.information(self, 'Completed', f'Check completed. {count} image(s) missing.')
        self.worker_thread = None
    
    def handle_error(self, error_msg):
        self.check_button.setEnabled(True)
        self.progress_bar.setValue(0)
        QMessageBox.critical(self, 'Error', f'Error during check: {error_msg}')
        self.worker_thread = None
    
    def save_log(self):
        if not hasattr(self, 'log') or not self.log:
            QMessageBox.warning(self, 'Error', 'No log to save. Run check first.')
            return
            
        default_file_name = f"{self.prefix_input.text().strip() or 'no_prefix'}missing_images.log"
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save Log File', default_file_name, 'Log Files (*.log);;All Files (*)')
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(self.log))
                QMessageBox.information(self, 'Success', 'Log file saved successfully.')
            except PermissionError as e:
                QMessageBox.critical(self, 'Error', f'Permission denied saving log: {str(e)}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to save log: {str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MissingImagesApp()
    window.show()
    sys.exit(app.exec_())
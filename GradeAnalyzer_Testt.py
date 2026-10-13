import tkinter as tk
from tkinter import ttk, messagebox


class GradeAnalyzerApp:
    def __init__(self, root):
        """
        ฟังก์ชันเริ่มต้น (Constructor)
        เรียกใช้เมื่อสร้างแอปพลิเคชัน ตั้งค่าหน้าต่างหลักและองค์ประกอบ UI
        """
        self.root = root
        self.root.title("ระบบวิเคราะห์ผลการเรียน (Student Grade Analyzer)")
        self.root.geometry("500x650")  # กำหนดขนาดหน้าต่าง
        self.root.configure(padx=20, pady=20)  # เพิ่มระยะขอบ

        # ตัวแปรเก็บข้อมูล
        self.student_name = tk.StringVar()
        self.math_score = tk.StringVar()
        self.science_score = tk.StringVar()
        self.english_score = tk.StringVar()
        self.history_score = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        """
        สร้างและจัดวางปุ่ม ช่องกรอกข้อความ และข้อความต่างๆ บนหน้าจอ
        """
        # ส่วนหัว (Header)
        title_label = ttk.Label(self.root, text="ระบบบันทึกและวิเคราะห์ผลการเรียน", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # กรอบสำหรับกรอกข้อมูล (Input Frame)
        input_frame = ttk.LabelFrame(self.root, text="ข้อมูลนักเรียน", padding=(10, 10))
        input_frame.pack(fill="x", pady=10)

        # ช่องกรอกชื่อ
        ttk.Label(input_frame, text="ชื่อ-นามสกุล:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(input_frame, textvariable=self.student_name, width=30).grid(row=0, column=1, sticky="w", pady=5,
                                                                              padx=10)

        # ช่องกรอกคะแนนแต่ละวิชา
        ttk.Label(input_frame, text="คะแนนคณิตศาสตร์ (0-100):").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(input_frame, textvariable=self.math_score, width=10).grid(row=1, column=1, sticky="w", pady=5,
                                                                            padx=10)

        ttk.Label(input_frame, text="คะแนนวิทยาศาสตร์ (0-100):").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(input_frame, textvariable=self.science_score, width=10).grid(row=2, column=1, sticky="w", pady=5,
                                                                               padx=10)

        ttk.Label(input_frame, text="คะแนนภาษาอังกฤษ (0-100):").grid(row=3, column=0, sticky="w", pady=5)
        ttk.Entry(input_frame, textvariable=self.english_score, width=10).grid(row=3, column=1, sticky="w", pady=5,
                                                                               padx=10)

        ttk.Label(input_frame, text="คะแนนประวัติศาสตร์ (0-100):").grid(row=4, column=0, sticky="w", pady=5)
        ttk.Entry(input_frame, textvariable=self.history_score, width=10).grid(row=4, column=1, sticky="w", pady=5,
                                                                               padx=10)

        # ปุ่มกดสำหรับประมวลผล
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", pady=15)

        analyze_btn = ttk.Button(button_frame, text="วิเคราะห์ผลการเรียน", command=self.analyze_grades)
        analyze_btn.pack(side="left", padx=5, expand=True, fill="x")

        clear_btn = ttk.Button(button_frame, text="ล้างข้อมูล", command=self.clear_inputs)
        clear_btn.pack(side="right", padx=5, expand=True, fill="x")

        # กรอบสำหรับแสดงผลลัพธ์ (Result Frame)
        self.result_frame = ttk.LabelFrame(self.root, text="สรุปผลการเรียน", padding=(10, 10))
        self.result_frame.pack(fill="both", expand=True, pady=10)

        # Text box สำหรับแสดงผลแบบหลายบรรทัด
        self.result_text = tk.Text(self.result_frame, height=12, width=40, font=("Courier", 12), state="disabled",
                                   bg="#f0f0f0")
        self.result_text.pack(fill="both", expand=True)

    def calculate_grade(self, score):
        """
        ฟังก์ชันสำหรับแปลงคะแนน (0-100) เป็นเกรด (A, B, C, D, F)
        """
        if score >= 80:
            return "A (4.0)"
        elif score >= 70:
            return "B (3.0)"
        elif score >= 60:
            return "C (2.0)"
        elif score >= 50:
            return "D (1.0)"
        else:
            return "F (0.0)"

    def calculate_gpa(self, average):
        """ คำนวณเกรดเฉลี่ยแบบคร่าวๆ จากคะแนนเฉลี่ยรวม """
        if average >= 80:
            return 4.0
        elif average >= 75:
            return 3.5
        elif average >= 70:
            return 3.0
        elif average >= 65:
            return 2.5
        elif average >= 60:
            return 2.0
        elif average >= 55:
            return 1.5
        elif average >= 50:
            return 1.0
        else:
            return 0.0

    def analyze_grades(self):
        """
        ฟังก์ชันนี้ทำงานเมื่อกดปุ่ม "วิเคราะห์ผลการเรียน"
        ทำหน้าที่: ดึงข้อมูล -> ตรวจสอบความถูกต้อง -> คำนวณ -> แสดงผล
        """
        name = self.student_name.get().strip()

        # 1. ตรวจสอบว่าใส่ชื่อหรือยัง
        if not name:
            messagebox.showwarning("คำเตือน", "กรุณากรอกชื่อนักเรียน")
            return

        try:
            # 2. แปลงค่าที่กรอกมาให้เป็นตัวเลขทศนิยม (float)
            math = float(self.math_score.get())
            science = float(self.science_score.get())
            english = float(self.english_score.get())
            history = float(self.history_score.get())

            # เก็บไว้ใน list เพื่อให้คำนวณง่าย
            scores = [math, science, english, history]
            subjects = ["คณิตศาสตร์", "วิทยาศาสตร์", "ภาษาอังกฤษ", "ประวัติศาสตร์"]

            # 3. ตรวจสอบว่าคะแนนต้องอยู่ระหว่าง 0-100
            for score in scores:
                if score < 0 or score > 100:
                    messagebox.showerror("ข้อผิดพลาด", "คะแนนต้องอยู่ระหว่าง 0 ถึง 100 เท่านั้น")
                    return

            # 4. คำนวณค่าเฉลี่ยและผลรวม
            total_score = sum(scores)
            average_score = total_score / len(scores)
            estimated_gpa = self.calculate_gpa(average_score)

            # 5. สร้างข้อความผลลัพธ์
            result_str = f"ชื่อ: {name}\n"
            result_str += "-" * 30 + "\n"

            # วนลูปเพื่อแสดงคะแนนและเกรดแต่ละวิชา
            for i in range(len(scores)):
                grade = self.calculate_grade(scores[i])
                # จัดรูปแบบข้อความให้ตรงกัน (ใช้ f-string)
                result_str += f"{subjects[i]:<15} {scores[i]:>6.2f} คะแนน (เกรด {grade})\n"

            result_str += "-" * 30 + "\n"
            result_str += f"คะแนนรวม: {total_score:.2f} / 400\n"
            result_str += f"คะแนนเฉลี่ย: {average_score:.2f} %\n"
            result_str += f"เกรดเฉลี่ยโดยประมาณ (GPA): {estimated_gpa:.2f}\n\n"

            # ประเมินผล
            if average_score >= 80:
                result_str += "สถานะ: ยอดเยี่ยมมาก! 🎉"
            elif average_score >= 50:
                result_str += "สถานะ: ผ่านเกณฑ์ ปกติ 👍"
            else:
                result_str += "สถานะ: ต้องปรับปรุง (ไม่ผ่านเกณฑ์) ⚠️"

            # 6. แสดงผลบน Text widget
            self.display_result(result_str)

        # จับข้อผิดพลาดถ้าผู้ใช้กรอกตัวอักษรแทนที่จะเป็นตัวเลข
        except ValueError:
            messagebox.showerror("ข้อผิดพลาด", "กรุณากรอกคะแนนเป็นตัวเลขเท่านั้น!")

    def display_result(self, text):
        """ ฟังก์ชันสำหรับอัพเดทข้อความในช่องแสดงผลลัพธ์ """
        self.result_text.config(state="normal")  # เปิดให้แก้ไขชั่วคราว
        self.result_text.delete(1.0, tk.END)  # ลบข้อความเก่า
        self.result_text.insert(tk.END, text)  # ใส่ข้อความใหม่
        self.result_text.config(state="disabled")  # ปิดการแก้ไข (ให้อ่านได้อย่างเดียว)

    def clear_inputs(self):
        """ ล้างข้อมูลในช่องกรอกทั้งหมด """
        self.student_name.set("")
        self.math_score.set("")
        self.science_score.set("")
        self.english_score.set("")
        self.history_score.set("")

        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state="disabled")


if __name__ == "__main__":
    # สร้างหน้าต่างหลักของ tkinter
    root = tk.Tk()

    # กำหนด theme เพื่อให้ UI ดูทันสมัยขึ้น (ถ้าใช้ Windows)
    try:
        from tkinter import ttk

        style = ttk.Style()
        style.theme_use('clam')  # 'clam', 'vista', 'windows'
    except:
        pass

    # สร้างแอปพลิเคชัน
    app = GradeAnalyzerApp(root)

    # รันโปรแกรมวนลูป (Event loop)
    root.mainloop()
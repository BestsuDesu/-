import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ----------------------------------------------------------------------
# ชุดสี (แก้ตรงนี้ได้ถ้าอยากเปลี่ยนธีม)
# ----------------------------------------------------------------------
BG = "#F5F3FF"           # พื้นหลังหลัก (ม่วงอ่อนมาก)
CARD = "#FFFFFF"         # พื้นการ์ด
PRIMARY = "#4F46E5"      # indigo
PRIMARY_DARK = "#4338CA"
SUCCESS = "#10B981"
SUCCESS_DARK = "#059669"
DANGER = "#EF4444"
DANGER_DARK = "#DC2626"
INFO = "#0EA5E9"
INFO_DARK = "#0284C7"
TEXT = "#1F2937"
MUTED = "#6B7280"

GRADE_COLORS = {
    "A": "#10B981",
    "B": "#3B82F6",
    "C": "#F59E0B",
    "D": "#F97316",
    "F": "#EF4444",
}

FONT = "Tahoma"
AUTOSAVE_PATH = os.path.join(os.path.expanduser("~"), ".grade_analyzer_autosave.json")
DEFAULT_SUBJECTS = ["คณิตศาสตร์", "วิทยาศาสตร์", "ภาษาอังกฤษ", "ประวัติศาสตร์"]


class GradeAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ระบบวิเคราะห์ผลการเรียน (Student Grade Analyzer)")
        self.root.geometry("720x860")
        self.root.minsize(640, 700)
        self.root.configure(bg=BG)

        self.student_name = tk.StringVar()
        self.subject_rows = []
        self.current_file = None  # ไฟล์ที่กำลังเปิด/บันทึกอยู่

        self.setup_styles()
        self.create_widgets()

        # ปุ่มลัด
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # โหลดข้อมูลครั้งล่าสุดอัตโนมัติ ถ้าไม่มีให้ใช้วิชาเริ่มต้น
        if not self.load_autosave():
            for name in DEFAULT_SUBJECTS:
                self.add_subject_row(name=name, credit="3")

    # ------------------------------------------------------------------
    # สไตล์ / ธีมสี
    # ------------------------------------------------------------------
    def setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD)
        style.configure("TLabel", background=BG, foreground=TEXT, font=(FONT, 10))
        style.configure("Card.TLabel", background=CARD, foreground=TEXT, font=(FONT, 10))
        style.configure("Head.TLabel", background=CARD, foreground=PRIMARY, font=(FONT, 10, "bold"))
        style.configure("Status.TLabel", background=BG, foreground=MUTED, font=(FONT, 9))

        style.configure("Card.TLabelframe", background=CARD, bordercolor=PRIMARY, relief="solid")
        style.configure("Card.TLabelframe.Label", background=CARD, foreground=PRIMARY,
                        font=(FONT, 11, "bold"))

        style.configure("TEntry", fieldbackground="#FFFFFF", foreground=TEXT,
                        bordercolor="#C7D2FE", lightcolor="#C7D2FE", darkcolor="#C7D2FE", padding=4)
        style.map("TEntry", bordercolor=[("focus", PRIMARY)], lightcolor=[("focus", PRIMARY)])

        def button_style(name, bg, hover):
            style.configure(name, background=bg, foreground="white", font=(FONT, 10, "bold"),
                            borderwidth=0, focusthickness=0, padding=(10, 7))
            style.map(name, background=[("active", hover), ("pressed", hover)],
                      foreground=[("active", "white")])

        button_style("Primary.TButton", PRIMARY, PRIMARY_DARK)
        button_style("Success.TButton", SUCCESS, SUCCESS_DARK)
        button_style("Danger.TButton", DANGER, DANGER_DARK)
        button_style("Info.TButton", INFO, INFO_DARK)
        style.configure("Small.Danger.TButton", padding=(6, 3), font=(FONT, 9, "bold"))

        style.configure("Vertical.TScrollbar", background="#C7D2FE", troughcolor=BG,
                        bordercolor=BG, arrowcolor=PRIMARY)

    # ------------------------------------------------------------------
    # สร้าง UI
    # ------------------------------------------------------------------
    def create_widgets(self):
        # แถบหัว (Banner)
        banner = tk.Frame(self.root, bg=PRIMARY)
        banner.pack(fill="x")
        tk.Label(banner, text="🎓  ระบบบันทึกและวิเคราะห์ผลการเรียน", bg=PRIMARY, fg="white",
                 font=(FONT, 17, "bold"), pady=14).pack()

        body = ttk.Frame(self.root, padding=(18, 12))
        body.pack(fill="both", expand=True)

        # แถบไฟล์ (เปิด / บันทึก / บันทึกเป็น)
        file_bar = ttk.Frame(body)
        file_bar.pack(fill="x", pady=(0, 8))
        ttk.Button(file_bar, text="📂 เปิดไฟล์", style="Info.TButton",
                   command=self.open_file).pack(side="left", padx=(0, 6))
        ttk.Button(file_bar, text="💾 บันทึก", style="Success.TButton",
                   command=self.save_file).pack(side="left", padx=(0, 6))
        ttk.Button(file_bar, text="บันทึกเป็น...", style="Info.TButton",
                   command=self.save_file_as).pack(side="left")

        # ข้อมูลนักเรียน
        name_frame = ttk.LabelFrame(body, text=" ข้อมูลนักเรียน ", style="Card.TLabelframe",
                                    padding=(12, 8))
        name_frame.pack(fill="x", pady=5)
        ttk.Label(name_frame, text="ชื่อ-นามสกุล:", style="Card.TLabel").grid(
            row=0, column=0, sticky="w")
        ttk.Entry(name_frame, textvariable=self.student_name, width=40).grid(
            row=0, column=1, sticky="w", padx=10, pady=4)

        # รายวิชา (มี scroll ถ้าวิชาเยอะ)
        subjects_box = ttk.LabelFrame(body, text=" รายวิชา ", style="Card.TLabelframe",
                                      padding=(8, 8))
        subjects_box.pack(fill="x", pady=5)

        self.canvas = tk.Canvas(subjects_box, bg=CARD, highlightthickness=0, height=210)
        scrollbar = ttk.Scrollbar(subjects_box, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.subjects_frame = ttk.Frame(self.canvas, style="Card.TFrame")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.subjects_frame,
                                                       anchor="nw")
        self.subjects_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind(
            "<Configure>", lambda e: self.canvas.itemconfigure(self.canvas_window, width=e.width))
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

        for col, text in enumerate(["ชื่อวิชา", "หน่วยกิต", "คะแนน (0-100)", "เกรด", ""]):
            ttk.Label(self.subjects_frame, text=text, style="Head.TLabel").grid(
                row=0, column=col, sticky="w", padx=6, pady=(0, 6))

        ttk.Button(body, text="＋ เพิ่มวิชา", style="Primary.TButton",
                   command=self.add_subject_row).pack(anchor="w", pady=(6, 0))

        # ปุ่มวิเคราะห์ / ล้างข้อมูล
        button_frame = ttk.Frame(body)
        button_frame.pack(fill="x", pady=12)
        ttk.Button(button_frame, text="📊 วิเคราะห์ผลการเรียน", style="Primary.TButton",
                   command=self.analyze_grades).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ttk.Button(button_frame, text="🧹 ล้างคะแนน", style="Danger.TButton",
                   command=self.clear_inputs).pack(side="right", expand=True, fill="x", padx=(6, 0))

        # ผลลัพธ์
        result_frame = ttk.LabelFrame(body, text=" สรุปผลการเรียน ", style="Card.TLabelframe",
                                      padding=(8, 8))
        result_frame.pack(fill="both", expand=True, pady=5)

        res_scroll = ttk.Scrollbar(result_frame, orient="vertical")
        self.result_text = tk.Text(result_frame, height=10, width=50, font=(FONT, 11),
                                   state="disabled", bg="#EEF2FF", fg=TEXT, relief="flat",
                                   padx=10, pady=8, yscrollcommand=res_scroll.set)
        res_scroll.config(command=self.result_text.yview)
        res_scroll.pack(side="right", fill="y")
        self.result_text.pack(side="left", fill="both", expand=True)

        # แท็กสีสำหรับข้อความผลลัพธ์
        self.result_text.tag_configure("name", font=(FONT, 13, "bold"), foreground=PRIMARY)
        self.result_text.tag_configure("subject", font=(FONT, 11, "bold"), foreground=TEXT)
        self.result_text.tag_configure("detail", foreground=MUTED)
        self.result_text.tag_configure("sep", foreground="#A5B4FC")
        self.result_text.tag_configure("summary", font=(FONT, 11, "bold"), foreground=TEXT)
        self.result_text.tag_configure("gpa", font=(FONT, 14, "bold"), foreground=PRIMARY)
        for letter, color in GRADE_COLORS.items():
            self.result_text.tag_configure(f"grade_{letter}", foreground=color,
                                           font=(FONT, 11, "bold"))
        self.result_text.tag_configure("status_good", foreground=SUCCESS,
                                       font=(FONT, 12, "bold"))
        self.result_text.tag_configure("status_ok", foreground=INFO, font=(FONT, 12, "bold"))
        self.result_text.tag_configure("status_bad", foreground=DANGER, font=(FONT, 12, "bold"))

        # แถบสถานะ
        self.status_var = tk.StringVar(value="ไฟล์: (ยังไม่ได้บันทึก)")
        ttk.Label(body, textvariable=self.status_var, style="Status.TLabel").pack(
            anchor="w", pady=(4, 0))

    # ------------------------------------------------------------------
    # Scroll ด้วยเมาส์
    # ------------------------------------------------------------------
    def _bind_mousewheel(self, _event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _unbind_mousewheel(self, _event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ------------------------------------------------------------------
    # จัดการแถววิชา
    # ------------------------------------------------------------------
    def add_subject_row(self, name="", credit="3", score=""):
        """ เพิ่มแถววิชาใหม่ (ชื่อวิชา, หน่วยกิต, คะแนน, เกรดแบบสด) """
        row = {
            "name": tk.StringVar(value=name),
            "credit": tk.StringVar(value=str(credit)),
            "score": tk.StringVar(value=str(score)),
        }
        f = self.subjects_frame
        row["name_entry"] = ttk.Entry(f, textvariable=row["name"], width=22)
        row["credit_entry"] = ttk.Entry(f, textvariable=row["credit"], width=8)
        row["score_entry"] = ttk.Entry(f, textvariable=row["score"], width=12)
        row["grade_label"] = tk.Label(f, text="-", width=4, bg=CARD, fg=MUTED,
                                      font=(FONT, 12, "bold"))
        row["remove_btn"] = ttk.Button(f, text="ลบ", style="Small.Danger.TButton", width=4,
                                       command=lambda r=row: self.remove_subject_row(r))

        # อัพเดทเกรดแบบสดเมื่อพิมพ์คะแนน
        row["score"].trace_add("write", lambda *_a, r=row: self.update_live_grade(r))

        self.subject_rows.append(row)
        self.regrid_rows()
        self.update_live_grade(row)
        if not name:
            row["name_entry"].focus_set()

    def regrid_rows(self):
        """ จัดวางแถวทั้งหมดใหม่ตามลำดับ """
        for i, r in enumerate(self.subject_rows, start=1):
            r["name_entry"].grid(row=i, column=0, padx=6, pady=3, sticky="w")
            r["credit_entry"].grid(row=i, column=1, padx=6, pady=3, sticky="w")
            r["score_entry"].grid(row=i, column=2, padx=6, pady=3, sticky="w")
            r["grade_label"].grid(row=i, column=3, padx=6, pady=3)
            r["remove_btn"].grid(row=i, column=4, padx=6, pady=3)

    def destroy_row_widgets(self, row):
        for key in ("name_entry", "credit_entry", "score_entry", "grade_label", "remove_btn"):
            row[key].destroy()

    def remove_subject_row(self, row):
        """ ลบแถววิชา (ต้องเหลืออย่างน้อย 1 วิชา) """
        if len(self.subject_rows) <= 1:
            messagebox.showwarning("คำเตือน", "ต้องมีอย่างน้อย 1 วิชา")
            return
        self.destroy_row_widgets(row)
        self.subject_rows.remove(row)
        self.regrid_rows()

    def clear_all_rows(self):
        for row in self.subject_rows:
            self.destroy_row_widgets(row)
        self.subject_rows = []

    def update_live_grade(self, row):
        """ แสดงเกรดสดข้างช่องคะแนน พร้อมสีตามเกรด """
        try:
            score = float(row["score"].get())
            if not 0 <= score <= 100:
                raise ValueError
            letter, _ = self.calculate_grade(score)
            row["grade_label"].config(text=letter, fg=GRADE_COLORS[letter])
        except ValueError:
            row["grade_label"].config(text="-", fg=MUTED)

    # ------------------------------------------------------------------
    # การคำนวณ
    # ------------------------------------------------------------------
    def calculate_grade(self, score):
        """ แปลงคะแนน (0-100) เป็น (ตัวอักษรเกรด, แต้มเกรด) """
        if score >= 80:
            return "A", 4.0
        elif score >= 70:
            return "B", 3.0
        elif score >= 60:
            return "C", 2.0
        elif score >= 50:
            return "D", 1.0
        else:
            return "F", 0.0

    def analyze_grades(self):
        """ ดึงข้อมูล -> ตรวจสอบ -> คำนวณ -> แสดงผล """
        name = self.student_name.get().strip()
        if not name:
            messagebox.showwarning("คำเตือน", "กรุณากรอกชื่อนักเรียน")
            return

        subjects = []  # (ชื่อวิชา, หน่วยกิต, คะแนน)
        try:
            for i, row in enumerate(self.subject_rows, start=1):
                subject_name = row["name"].get().strip()
                if not subject_name:
                    messagebox.showwarning("คำเตือน", f"กรุณากรอกชื่อวิชาในแถวที่ {i}")
                    return

                credit = float(row["credit"].get())
                score = float(row["score"].get())

                if credit <= 0:
                    messagebox.showerror("ข้อผิดพลาด",
                                         f"หน่วยกิตของวิชา \"{subject_name}\" ต้องมากกว่า 0")
                    return
                if score < 0 or score > 100:
                    messagebox.showerror("ข้อผิดพลาด",
                                         f"คะแนนของวิชา \"{subject_name}\" ต้องอยู่ระหว่าง 0 ถึง 100")
                    return

                subjects.append((subject_name, credit, score))
        except ValueError:
            messagebox.showerror("ข้อผิดพลาด", "กรุณากรอกหน่วยกิตและคะแนนเป็นตัวเลขเท่านั้น!")
            return

        total_credits = sum(c for _, c, _ in subjects)
        total_points = 0.0
        weighted_score = 0.0

        # สร้างผลลัพธ์เป็นชุดของ (ข้อความ, แท็กสี)
        segments = [(f"👤 {name}\n", "name"), ("─" * 40 + "\n", "sep")]
        for subject_name, credit, score in subjects:
            letter, point = self.calculate_grade(score)
            total_points += point * credit
            weighted_score += score * credit
            segments.append((f"{subject_name}\n", "subject"))
            segments.append((f"   หน่วยกิต {credit:g}  |  คะแนน {score:.2f}  |  เกรด ", "detail"))
            segments.append((f"{letter} ({point:.1f})\n", f"grade_{letter}"))

        gpa = total_points / total_credits
        average_score = weighted_score / total_credits

        segments.append(("─" * 40 + "\n", "sep"))
        segments.append((f"จำนวนวิชา: {len(subjects)} วิชา\n", "summary"))
        segments.append((f"หน่วยกิตรวม: {total_credits:g}\n", "summary"))
        segments.append((f"คะแนนเฉลี่ย (ถ่วงน้ำหนักหน่วยกิต): {average_score:.2f} %\n", "summary"))
        segments.append((f"เกรดเฉลี่ย (GPA): {gpa:.2f}\n\n", "gpa"))

        if gpa >= 3.5:
            segments.append(("สถานะ: ยอดเยี่ยมมาก! 🎉", "status_good"))
        elif gpa >= 1.0:
            segments.append(("สถานะ: ผ่านเกณฑ์ ปกติ 👍", "status_ok"))
        else:
            segments.append(("สถานะ: ต้องปรับปรุง (ไม่ผ่านเกณฑ์) ⚠️", "status_bad"))

        self.display_result(segments)

    def display_result(self, segments):
        """ แสดงผลลัพธ์พร้อมสี (segments = [(text, tag), ...]) """
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        for text, tag in segments:
            self.result_text.insert(tk.END, text, tag)
        self.result_text.config(state="disabled")

    def clear_result(self):
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state="disabled")

    def clear_inputs(self):
        """ ล้างคะแนนทั้งหมด (คงชื่อ รายวิชา และหน่วยกิตไว้) """
        for row in self.subject_rows:
            row["score"].set("")
        self.clear_result()

    # ------------------------------------------------------------------
    # บันทึก / เปิดไฟล์
    # ------------------------------------------------------------------
    def collect_data(self):
        """ รวบรวมข้อมูลปัจจุบันเป็น dict (ไม่ต้อง validate เพื่อให้เซฟงานค้างได้) """
        return {
            "student_name": self.student_name.get(),
            "subjects": [
                {
                    "name": r["name"].get(),
                    "credit": r["credit"].get(),
                    "score": r["score"].get(),
                }
                for r in self.subject_rows
            ],
        }

    def apply_data(self, data):
        """ นำข้อมูลจาก dict มาใส่ใน UI """
        self.student_name.set(data.get("student_name", ""))
        self.clear_all_rows()
        subjects = data.get("subjects", [])
        for s in subjects:
            self.add_subject_row(name=s.get("name", ""), credit=s.get("credit", "3"),
                                 score=s.get("score", ""))
        if not self.subject_rows:
            self.add_subject_row(credit="3")
        self.clear_result()

    def write_json(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.collect_data(), f, ensure_ascii=False, indent=2)

    def set_current_file(self, path):
        self.current_file = path
        if path:
            self.status_var.set(f"ไฟล์: {path}")
            self.root.title(f"ระบบวิเคราะห์ผลการเรียน - {os.path.basename(path)}")
        else:
            self.status_var.set("ไฟล์: (ยังไม่ได้บันทึก)")
            self.root.title("ระบบวิเคราะห์ผลการเรียน (Student Grade Analyzer)")

    def save_file(self):
        """ บันทึกทับไฟล์เดิม ถ้ายังไม่มีไฟล์จะถามชื่อใหม่ """
        if not self.current_file:
            return self.save_file_as()
        try:
            self.write_json(self.current_file)
            self.status_var.set(f"✅ บันทึกแล้ว: {self.current_file}")
        except OSError as e:
            messagebox.showerror("ข้อผิดพลาด", f"บันทึกไฟล์ไม่สำเร็จ\n{e}")

    def save_file_as(self):
        path = filedialog.asksaveasfilename(
            title="บันทึกข้อมูลผลการเรียน",
            defaultextension=".json",
            initialfile=(self.student_name.get().strip() or "grades") + ".json",
            filetypes=[("ไฟล์ข้อมูลผลการเรียน (JSON)", "*.json"), ("ทุกไฟล์", "*.*")],
        )
        if not path:
            return
        try:
            self.write_json(path)
            self.set_current_file(path)
            self.status_var.set(f"✅ บันทึกแล้ว: {path}")
        except OSError as e:
            messagebox.showerror("ข้อผิดพลาด", f"บันทึกไฟล์ไม่สำเร็จ\n{e}")

    def open_file(self):
        path = filedialog.askopenfilename(
            title="เปิดไฟล์ข้อมูลผลการเรียน",
            filetypes=[("ไฟล์ข้อมูลผลการเรียน (JSON)", "*.json"), ("ทุกไฟล์", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("รูปแบบไฟล์ไม่ถูกต้อง")
            self.apply_data(data)
            self.set_current_file(path)
        except (OSError, ValueError) as e:
            messagebox.showerror("ข้อผิดพลาด", f"เปิดไฟล์ไม่สำเร็จ\n{e}")

    # ------------------------------------------------------------------
    # บันทึกอัตโนมัติ (เปิดโปรแกรมครั้งหน้าข้อมูลจะกลับมาเอง)
    # ------------------------------------------------------------------
    def load_autosave(self):
        try:
            with open(AUTOSAVE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict) or not data.get("subjects"):
                return False
            self.apply_data(data)
            return True
        except (OSError, ValueError):
            return False

    def on_close(self):
        try:
            self.write_json(AUTOSAVE_PATH)
        except OSError:
            pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = GradeAnalyzerApp(root)
    root.mainloop()
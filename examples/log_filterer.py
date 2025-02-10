from enum import Enum
import re

class ChannelTypes(Enum):
    Personal = "Personal"
    Commercial = "Commercial"

class Log:
    project: str
    log: str
    date: str
    time: str
    log_type: str

class LogLine(Log):
    parts: list[str] = []

    def __init__(self, log_line: str):
        if not log_line:
            raise ValueError("Log line is empty")
        
        if not log_line.startswith("["):
            raise ValueError("Log line is not a valid log line")

        self.parts = self._regex_matches(log_line)
        self.date = self.parts[0].split(" ")[0]
        self.time = self.parts[0].split(" ")[1]
        self.log_type = self.parts[2].strip()

    @staticmethod
    def _regex_matches(log_line: str) -> list[str]:
        pattern = r"\[(.*?)\]"
        matches = re.findall(pattern, log_line.strip())
        if matches[-1] == "":
            matches = matches[:-1]
        return matches

class PersonalLogLine(LogLine):
    customer_no: str
    
    def __init__(self, line):
        super().__init__(line)
        self.customer_no = self.parts[3].split("Cust: ")[1] if "Cust" in self.parts[3] else "Anon"
        self.project = self.parts[4] if "S:" in self.parts[4] else "No Project"
        self.log = "@@".join(self.parts[5:])

    def __str__(self):
        return f"{self.date},{self.time},{self.log_type},{self.project},{self.customer_no},{self.log}"

class CommercialLogLine(LogLine):
    corporate_no: str

    def __init__(self, line):
        super().__init__(line)
        self.customer_no = self.parts[3].split("Cust: ")[1] if "Cust" in self.parts[3] else "Anon"
        self.corporate_no = self.parts[4].split("Corp: ")[1] if "Corp" in self.parts[4] else "Anon"
        self.project = self.parts[5] if "S:" in self.parts[5] else "No Project"
        self.log = "@@".join(self.parts[6:])


    def __str__(self):
        return f"{self.date},{self.time},{self.log_type},{self.project},{self.customer_no},{self.corporate_no},{self.log}"

def log_filterer(log_file_path: str, project_name: str, get_if_in_line: bool, inline_str: str, channel_type: ChannelTypes) -> str:
    with open(log_file_path, "r", encoding="utf-8-sig") as log_file:
        log_lines = log_file.readlines()

    logs: list[LogLine] = []
    buffer = ""  # Logları birleştirmek için kullanılacak geçici değişken

    for item in log_lines[6:]:
        buffer += item  # Satırı geçici değişkene ekle

        if item.strip().endswith("]"):  # Eğer satır ] ile bitiyorsa, tam bir log satırıdır.
            if channel_type == ChannelTypes.Commercial:
                log = CommercialLogLine(buffer)
            else:
                log = PersonalLogLine(buffer)

            if log.project.lower() == f"S:{project_name}".lower() or (get_if_in_line and inline_str in log.log):
                logs.append(log)

            buffer = ""  # Bir sonraki log için buffer sıfırla
            
    if channel_type == ChannelTypes.Commercial:
        headers = "Date,Time,Log Type,Project,Customer Number,Corporate Number,Log"
    elif channel_type == ChannelTypes.Personal:
        headers = "Date,Time,Log Type,Project,Customer Number,Log"

    # CSV oluşturma
    csv = headers + "\n" + "\n".join(str(log) for log in logs)

    output_file_name = f"{log_file_path}_filtered_logs.csv"
    with open(output_file_name, "w", encoding="utf-8-sig") as csv_file:
        csv_file.write(csv)

    return f"Filtered logs saved to file [{output_file_name}] successfully"

settings = {
    "name": "Log Filterer",
    "enabled": True,
    "description": "Filters log by project name or log content",
    "tags": ["log", "filter", "project", "content"]
}


if __name__ == "__main__":
    print(log_filterer("logs.txt", "AutomaticPaymentInstruction", True, "AutomaticPaymentInstruction", ChannelTypes.Commercial))

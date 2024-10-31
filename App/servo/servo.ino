#include <Servo.h>

int pos1 = 90; // Vị trí ban đầu cho servo 1
int pos2 = 90; // Vị trí ban đầu cho servo 2

Servo myservo1;  // tạo đối tượng servo để điều khiển servo đầu tiên
Servo myservo2;  // tạo đối tượng servo để điều khiển servo thứ hai

void setup() {
  myservo1.attach(9);  // gắn servo đầu tiên vào chân 9
  myservo2.attach(10); // gắn servo thứ hai vào chân 10
  Serial.begin(9600);  // bắt đầu giao tiếp serial với tốc độ baud 9600

  // Đặt các servo về vị trí ban đầu
  myservo1.write(pos1); 
  myservo2.write(pos2);
}

void loop() {
  if (Serial.available() > 0) { // kiểm tra xem có dữ liệu gửi tới Arduino không
    char command = Serial.read(); // đọc dữ liệu dưới dạng ký tự

    switch(command) {
      case '1':
        pos1 = min(pos1 + 5, 180); // Giới hạn tối đa là 180 độ
        myservo1.write(pos1); // di chuyển servo đầu tiên về bên phải 5 độ
        break;
      case '2':
        pos1 = max(pos1 - 5, 0); // Giới hạn tối thiểu là 0 độ
        myservo1.write(pos1); // di chuyển servo đầu tiên về bên trái 5 độ
        break;
      case '3':
        pos2 = min(pos2 + 5, 180); // Giới hạn tối đa là 180 độ
        myservo2.write(pos2); // di chuyển servo thứ hai về bên phải 5 độ
        break;
      case '4':
        pos2 = max(pos2 - 5, 0); // Giới hạn tối thiểu là 0 độ
        myservo2.write(pos2); // di chuyển servo thứ hai về bên trái 5 độ
        break;
      default:
        break;
    }

    // Xóa buffer serial
    while (Serial.available() > 0) {
      Serial.read();
    }
  }
}

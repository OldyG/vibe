package com.example.types;

public record Person(String name, int age) {
  public Person {
    if (age < 0) {
      throw new IllegalArgumentException();
    }
  }

  public String label() {
    return name + age;
  }
}

enum Status {
  OK, FAIL;

  public boolean isOk() {
    return this == OK;
  }
}

interface Worker {
  void run();
  default int priority() { return 1; }
}

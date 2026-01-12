package com.example;

public class SimpleClass {
  /** Count of items. */
  private int count;

  public SimpleClass() {
    this.count = 0;
  }

  /** Does work. */
  public String doWork(int a, String b) throws Exception {
    return a + b;
  }

  class Inner {
    void innerMethod() {}
  }
}

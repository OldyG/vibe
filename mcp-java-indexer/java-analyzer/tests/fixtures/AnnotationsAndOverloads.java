package com.example;

public class AnnotationsAndOverloads {
  @Deprecated
  public void doThing() {}

  @Deprecated
  public void doThing(int a) {}

  @MyAnno(
    value = "x",
    flag = true
  )
  protected final int value = 42;
}

@interface MyAnno {
  String value();
  boolean flag();
}
